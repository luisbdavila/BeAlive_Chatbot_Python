import sqlite3
from typing import Type
import numpy as np
import torch
import streamlit as st
from langchain.tools import BaseTool
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from BeAlive.data.loader import get_sqlite_database_path
from BeAlive.chatbot.chains.check_activity_id import GetActivityIDChain
from BeAlive.chatbot.chains.check_rating import GetRatingChain
from BeAlive.chatbot.chains.check_review import GetReviewChain


class ActivityReviewInfo(BaseModel):
    """
    Model for input of ReviewActivityTool.
    """

    review: str
    activity_name: str
    rating: int


class ReviewActivityTool(BaseTool):
    """
    A tool for reviewing activities that a user attended or reviewing a user
    that attended an activity.

    Attributes:
    ----------
        name : str
            The name of the tool.
        description : str
            A description of the tool's purpose.
        args_schema : Type[BaseModel]
            The schema for the input arguments of the tool.
        return_direct : bool
            Whether to return the result directly or not.

    Methods:
    -------
        _run(self, **kwargs) -> str:
            Executes the tool's functionality.

    """
    name: str = "ReviewActivitesTools"
    description: str = "Review an activity."
    args_schema: Type[BaseModel] = ActivityReviewInfo
    return_direct: bool = True

    def _run(self, **kwargs) -> str:

        """
        Review an activity that a user attended or reviewing a user that
        attended an activity.

        Parameters:
        ----------
            **kwargs : dict
                Keyword arguments containing the input data for the tool.

        Returns:
        -------
                str
                    The result of the tool's execution.
        """

        db_path = get_sqlite_database_path()
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        user_id = st.session_state.user_id

        try:
            rating = GetRatingChain().invoke({"user_input": kwargs.get("rating", -1)})

            review = GetReviewChain().invoke({"user_input": kwargs.get("review", 'No review')})

        except:
            return "An error occurred."

        try:
            cursor.execute("""SELECT a.activity_id, a.activity_name
                                FROM activities a JOIN reservations r
                                ON a.activity_id = r.activity_id
                                WHERE r.user_id = ? AND r.state = 'confirmed'
                                AND a.activity_state = 'finished'
                           """, (user_id,))
            activity_list = cursor.fetchall()

            activity_id = GetActivityIDChain().invoke({"user_input": kwargs.get("activity_name", "No activity"),
                                                      'activity_list': str(activity_list)})

            if activity_id.activity_id == -1:
                return "An error occurred. You haven't attended any activities with that name."

            cursor.execute("""SELECT cumulative_rating, host_id
                                FROM activities
                                WHERE activity_id = ? and 
                                activity_state = 'finished' """,
                           (activity_id.activity_id,))

            cumulative_rating_act = cursor.fetchone()
            host_id = cumulative_rating_act[1]

        except:
            return "An error occurred while retrieving the activity information."

        finally:
            cursor.close()
            connection.close()

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
            model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

            inputs = tokenizer(review.review, return_tensors="pt",
                               truncation=True, padding=True)

            outputs = model(**inputs)
            logits = outputs.logits

            score = torch.softmax(logits, dim=1)[0][1].item()

            if rating.rating == -1:
                rating.rating = round(score*5)
                cumulative_rating_activity = 0.5 * cumulative_rating_act[0] + 0.5 * (score*5)
            else:
                cumulative_rating_activity = 0.5 * cumulative_rating_act[0] + 0.5 * np.mean([float(rating.rating), (score * 5)])

            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            try:
                cursor.execute("""SELECT cumulative_rating from users
                               WHERE user_id = ?""", (host_id,))
                cumulative_rating_host = cursor.fetchone()

            except:
                return "An error occurred while retrieving the user info."
            finally:
                cursor.close()
                connection.close()

            host_cumulative_rating_new = 0.9 * cumulative_rating_host[0] + 0.1 * cumulative_rating_activity

            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()

            try:
                cursor.execute("""INSERT INTO review_activity (activity_id,
                               user_id , review , rating)
                                VALUES (?, ?, ?, ?)""",
                               (activity_id.activity_id,
                                user_id,
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
                cursor.execute("""UPDATE activities SET cumulative_rating = ?
                               WHERE activity_id = ?""",
                               (cumulative_rating_activity,
                                activity_id.activity_id))
                connection.commit()
            except:
                return "An error occurred while updating the activity rating."

            finally:
                cursor.close()
                connection.close()

            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            try:
                cursor.execute("""UPDATE users SET cumulative_rating = ?
                               WHERE user_id = ?""",
                               (host_cumulative_rating_new, host_id))
                connection.commit()
            except:
                return "An error occurred while updating the host rating."
            finally:
                cursor.close()
                connection.close()

        except:
            return "An error occurred while updating the cumulative rating."

        return "The review was inserted successfully"
