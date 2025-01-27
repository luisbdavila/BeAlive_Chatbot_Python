from pinecone import Pinecone


class UserDatabase:
    """
    Class to interact with SQLite database table 'users'.

    Schema:
    --------
    - id: INTEGER PRIMARY KEY AUTOINCREMENT
    - username: TEXT NOT NULL
    - password: TEXT NOT NULL
    - name: TEXT
    - birthday: DATE
    - email: TEXT UNIQUE NOT NULL
    - phone_number: TEXT
    - location: TEXT
    - interests: TEXT
    - cumulative_rating: REAL DEFAULT 0

    This class provides methods verifying and retrieving user data.
    Methods:
    --------
    __init__(conn)
        Initialize the UserDatabase instance.
    check_if_email_exists(email)
        Check if an email already exists in the database.
    add_user(username, password, name, birthday, email, phone_number, location, interests, cumulative_rating)
        Add a new user to the database.
    delete_user(user_id)
        Delete a user from the database.
    verify_user(username, password)
        Verify if a user exists.
    get_user_details(username)
        Retrieve detailed information about a user by their username.
    get_user_id(username)
        Retrieve the user ID based on the username.
    check_if_username_exists(username)
        Check if an username already exists in the database.
    get_user_details(username)
        Retrieve detailed information about a user by their username.
    update_user(username, **kwargs)
        Update user information in the database.
    """

    def __init__(self, conn):
        """
        Initialize the UserDatabase instance.

        Parameters:
        ----------
            conn: sqlite3.Connection
                SQLite database connection object.
        """
        self.conn = conn

    def check_if_email_exists(self, email):
        """
        Check if an email already exists in the database.

        Parameters:
        ----------

            email :str
                Email address to check.

        Returns:
        ----------
            True if the email exists, False otherwise.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT email FROM users WHERE email = :email",
                {"email": email}
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def add_user(self,
                 username,
                 password,
                 name,
                 birthday,
                 email,
                 phone_number,
                 location,
                 interests,
                 cumulative_rating):
        """
        Add a new user to the database.

        Parameters:
        ----------
            username: str
                User's  username.
            password: str
                User's password (hashed).
            name: str
                User's name.
            birthday: str
                User's birthday.
            email: str
                User's email address.
            phone_number: str
                User's phone number.
            location: str
                User's location.
            interests: str
                User's interests.
            cumulative_rating: int
                Cumulative rating of user (= 0)

        Returns:
        ----------
            True if the user was added successfully, False otherwise.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO users (username, password, name, birthday, email,
                                    phone_number, location, interests ,
                                    cumulative_rating)
                VALUES (:username, :password, :name, :birthday, :email,
                        :phone_number, :location, :interests,
                        :cumulative_rating)
                """,
                {
                    "username": username,
                    "password": password,
                    "name": name,
                    "birthday": birthday,
                    "email": email,
                    "phone_number": phone_number,
                    "location": location,
                    "interests": interests,
                    "cumulative_rating": cumulative_rating,
                },
            )
            self.conn.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()

    def delete_user(self, user_id):
        """
        Delete a user from the database.

        Parameters:
        ----------
            username: str
                User's username.
        Returns:
        ----------
            True if the user was deleted successfully, False otherwise.
        """

        cursor = self.conn.cursor()

        try:
            pinecone = Pinecone()
            pinecone_index = pinecone.Index("activities")

            cursor.execute("SELECT activity_id FROM activities WHERE host_id = :user_id", {"user_id": user_id})
            activity_ids = [str(row[0]) for row in cursor.fetchall()]

            # Step 2: Delete reviews in review_user and review_activity linked to this user
            cursor.execute("DELETE FROM review_user WHERE user_id = :user_id or host_id = :host_id", {"user_id": user_id,
                                                                                                      "host_id": user_id})
            self.conn.commit()

            cursor.execute("DELETE FROM review_activity WHERE user_id = :user_id", {"user_id": user_id})
            self.conn.commit()

            # Step 3: Delete reservations linked to this user
            cursor.execute("DELETE FROM reservations WHERE user_id = :user_id or host_id = :host_id", {"user_id": user_id,
                                                                                                       "host_id": user_id})
            self.conn.commit()
            # Step 4: Delete activities hosted by this user
            cursor.execute("DELETE FROM activities WHERE host_id = :user_id", {"user_id": user_id})
            self.conn.commit()

            if activity_ids:
                pinecone_index.delete(ids=activity_ids)

            # Step 5: Finally, delete the user from the users table
            cursor.execute("DELETE FROM users WHERE user_id = :user_id", {"user_id": user_id})
            self.conn.commit()

            return True
        except Exception:
            return False
        finally:
            cursor.close()

    def verify_user(self, username, password):
        """
        Verify if a user exists with the provided username and password.

        Parameters:
        ----------
            email: str
                User's email address.
            password: str
                User's password (hashed).

        Returns:
        ----------
            True if the user is verified, False otherwise.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """SELECT user_id FROM users WHERE username = :username AND
                                                password = :password""",
                {"username": username, "password": password},
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def get_user_id(self, username):
        """
        Retrieve the ID of a user by their username.

        Parameters:
        ----------
            username: str
                User's username.

        Returns:
        ----------
            User ID if found, None otherwise.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT user_id FROM users WHERE username = :username",
                {"username": username}
            )
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()

    def check_if_username_exists(self, username):
        """
        Check if an username already exists in the database.

        Parameters:
        ----------
            username: str
                username to check.

        Returns:
        ----------
            True if the username exists, False otherwise.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "SELECT username FROM users WHERE username = :username",
                {"username": username}
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def get_user_details(self, username):
        """
        Retrieve detailed information about a user by their username.

        Parameters:
        ----------
            Username: str
                User's username.

        Returns:
        ----------
            User details (username, password, name, birthday,
                                        email, phone_number, location,
                                        interests , cumulative_rating)
            if found, None otherwise.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """SELECT username, password, name, birthday, email,
                          phone_number, location, interests ,
                          cumulative_rating
                FROM users WHERE username = :username""",
                {"username": username},
            )
            return cursor.fetchone()
        finally:
            cursor.close()

    def update_user(self, username, **kwargs):
        """
        Update user information in the database.

        Parameters:
        ----------
            email: str
                username of the user to update.
            **kwargs:
                Key-value pairs representing the fields to update.

        Returns:
        ----------
            True if a user was updated, False otherwise.
        """
        cursor = self.conn.cursor()

        allowed_fields = {"password", "email", "phone_number", "location",
                          "interests"}

        filtered_kwargs = {keys: values for keys, values in kwargs.items() if keys in allowed_fields}

        if len(filtered_kwargs) == 0:
            print("No valid fields to update.")
            return False

        try:
            update_fields = ", ".join([f"{k} = :{k}" for k in filtered_kwargs.keys()])
            query = f"UPDATE users SET {update_fields} WHERE username = :username"
            cursor.execute(query, {**filtered_kwargs, "username": username})
            self.conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
