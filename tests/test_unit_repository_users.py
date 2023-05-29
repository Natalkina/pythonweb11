import unittest

from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar
from src.database.models import User
from src.schemas import UserModel


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_user_by_email(self):
        user = User(email='test@test.com')
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = user

        with patch.object(self.session, 'query', return_value=mock_query):
            find_user = await get_user_by_email(email='test@example.com', db=self.session)
            self.assertEqual(find_user.email, user.email)

    async def test_create_user(self):
        body = UserModel(
            email="testqqq@test.com",
            username="testtt",
            password="Test123",
            confirmed=False
        )

        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        user = User(refresh_token='test123')

        new_token = 'test321'

        await update_token(user=user, token=new_token, db=self.session)

        self.assertEqual(user.refresh_token, new_token)

    async def test_confirmed_email(self):
        user = User(email='test@example.com')

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = user

        with patch.object(self.session, 'query', return_value=mock_query):
            await confirmed_email(email='test@example.com', db=self.session)
            self.assertEqual(user.email, user.email)
            self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        user = User(email='test@instance.com', avatar='https://instance.com/avatar.jpg')

        new_avatar_url = 'https://instance.com/new_avatar.jpg'
        await update_avatar(email='test@example.com', url=new_avatar_url, db=self.session)

        updated_user = await get_user_by_email(email='test@example.com', db=self.session)

        self.assertEqual(updated_user.avatar, new_avatar_url)


if __name__ == '__main__':
    unittest.main()

