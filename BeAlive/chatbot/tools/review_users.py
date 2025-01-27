import sqlite3
from typing import Type
import streamlit as st
from langchain.tools import BaseTool
from BeAlive.data.loader import get_sqlite_database_path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from pydantic import BaseModel
import numpy as np
from BeAlive.chatbot.chains.check_activity_id import GetActivityIDChain
from BeAlive.chatbot.chains.check_reservation_user_id import GetReservationUserIDChain
from BeAlive.chatbot.chains.check_rating import GetRatingChain
from BeAlive.chatbot.chains.check_review import GetReviewChain


class UserReviewInfo(BaseModel):
    """
    Represents the input model for reviewing a user.

    Attributes:
    ----------
        user : str
            The name of the user.
        review : str
            The review about the user.
        activity_name : str
            The name of the activity.
        rating : int
            The rating given to the user.
    """
    user: str
    review: str
    activity_name: str
    rating: int


class ReviewUsersTool(BaseTool):
    """
    Tool to review a user and update their cumulative rating.

    Attributes:
    -----------
    name : str
        The name of the tool.
    description : str
        The description of the tool.
    args_schema : Type[BaseModel]
        The chema for the input arguments.
    return_direct : bool
        Whether to return the result directly or not.

    Methods:
    --------
    _run(self, **kwargs) -> str:
        Processes the user review and updates their
        rating and review details in the database.

    """
    name: str = "ReviewUsersTool"
    description: str = "Review users and score."
    args_schema: Type[BaseModel] = UserReviewInfo
    return_direct: bool = True

    def _run(self, **kwargs) -> str:
        """
        Processes the user review and updates their
        rating and review details in the database.

        Parameters:
        -----------
        **kwargs : dict
            Dictionary containing the user input arguments.

        Returns:
        --------
        str
            A message indicating the result of the review process
            (success, error, or status updates).

        """
        db_path = get_sqlite_database_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        host_id = st.session_state.user_id

        try:

            rating = GetRatingChain().invoke({
                "user_input": kwargs.get('rating', -1)})

            review = GetReviewChain().invoke({
                "user_input": kwargs.get('review', 'No review')})

        except:
            return "An error occurred."

        try:

            cursor.execute("""SELECT activity_id, activity_name
                                FROM activities
                                WHERE host_id = ? and
                                activity_state = 'finished'""", (host_id,))
            activity_list = cursor.fetchall()
            activity_id = GetActivityIDChain().invoke({
                "user_input": kwargs.get("activity_name", "No activity"),
                'activity_list': str(activity_list)})

            if activity_id.activity_id == -1:
                return "An error occurred. You don't have any activities with that name."
        except:
            return "An error occurred. Please be more clear."

        finally:
            cursor.close()
            connection.close()

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT r.user_id, u.username
                            FROM reservations r JOIN users u
                                on r.user_id = u.user_id
                            WHERE r.activity_id = ? and r.state = 'confirmed'
                           """, (activity_id.activity_id,))
            reservation_user_list = cursor.fetchall()

            user_id = GetReservationUserIDChain().invoke({
                'user_input': kwargs.get("user", "No user"),
                'reservation_list': str(reservation_user_list)})

            if user_id.user_id == -1:
                return "An error occurred. You don't have any participants with that username for that activity."

        except:
            return "An error occurred."

        finally:
            cursor.close()
            connection.close()

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            cursor.execute(""" SELECT activity_state 
                                FROM activities
                                WHERE activity_id = ?""",
                                  (activity_id.activity_id,))

            activity_state = cursor.fetchone()

        except:
            return "An error occurred while retrieving the state of the activity."

        finally:
            cursor.close()
            connection.close()


        try:
            if activity_state[0] != "finished":
                return "The activity is active. You cannot review users."

            else:
                tokenizer = AutoTokenizer.from_pretrained(
                    "distilbert-base-uncased-finetuned-sst-2-english")
                model = AutoModelForSequenceClassification.from_pretrained(
                    "distilbert-base-uncased-finetuned-sst-2-english")

                inputs = tokenizer(review.review, return_tensors="pt",
                                    truncation=True, padding=True)

                outputs = model(**inputs)
                logits = outputs.logits

                score = torch.softmax(logits, dim=1)[0][1].item()

                if score < 0.2:
                    score = 0.2

                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()

                try:
                    cursor.execute("""SELECT cumulative_rating 
                                   FROM users WHERE user_id = ?""",
                                     (user_id.user_id,))
                    cumulative_rating = cursor.fetchone()

                except:
                    return "An error occurred while retrieving the cumulative rating. torch"

                finally:
                    cursor.close()
                    connection.close()

                if rating.rating != -1:
                    final_score = (0.8 * cumulative_rating[0]) + 0.2 * np.mean(
                        [float(rating.rating), (score * 5)])
                else:
                    rating.rating = round(score*5)      
                    final_score = (0.8 * cumulative_rating[0]) + 0.2 * (
                        score*5)

                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                try:
                    cursor.execute("""INSERT INTO review_user
                                   (host_id, activity_id, user_id ,
                                    review , rating)
                                    VALUES (?, ?, ?, ?, ?)""",
                                      (host_id,
                                        activity_id.activity_id,
                                        user_id.user_id,
                                        review.review,
                                        rating.rating))

                    connection.commit()
                except:
                    return "An error occurred while inserting the review."
                finally:
                    cursor.close()
                    connection.close()

                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                try:
                    cursor.execute("""UPDATE users SET cumulative_rating = ?
                                   WHERE user_id = ?""",
                                     (final_score, user_id.user_id))
                    connection.commit()
                except:
                    return "An error occurred while updating the cumulative rating."

                finally:
                    cursor.close()
                    connection.close()

        except:
            return "An error occurred while updating the rating."

        return "The review was inserted successfully"
