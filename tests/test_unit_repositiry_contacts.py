import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.schemas import ContactModel, ContactUpdate, ContactStatusUpdate
from src.database.models import Contact, User
from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    create_contact,
    update_contact,
    get_contacts_by,
    get_contacts_birthdays,
    remove_contact
    )


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    def tearDown(self):
        pass

    async def test_get_contacts(self):
        contacts = [Contact() for _ in range(3)]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_exist(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_exist(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact_by_id(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(
            name="test",
            surname="Tested",
            email="test@test.com",
            mobile="0677833421",
            date_of_birth="2000-02-25"
        )

        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.mobile, body.mobile)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertEqual(result.user_id, self.user.id)
        self.assertTrue(hasattr(result, "id"))

    async def test_create_contact_with_exception(self):
        body = ContactModel(
            name="test",
            surname="Tested",
            email="test@test.com",
            mobile="0677833421",
            date_of_birth="2000-02-25"
        )


        self.session.add.side_effect = Exception("Some error message")


        with self.assertRaises(ValueError) as context:
            await create_contact(body=body, user=self.user, db=self.session)

            self.assertEqual(str(context.exception), "Failed to create user")
            self.session.rollback.assert_called_once()



    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactModel(
            name="test",
            surname="TestContact",
            email="test@test.com",
            mobile="0932323321",
            date_of_birth="2000-05-26"
        )

        contact = Contact(
            name="test2",
            surname="TestContact2",
            email="test2@test.com",
            mobile="0932222222",
            date_of_birth="2000-05-23"
        )

        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(body=body, contact_id=1, user=self.user, db=self.session)

        self.assertEqual(result, contact)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.mobile, body.mobile)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_not_found(self):
        body = ContactModel(
            name="test3",
            surname="TestContact3",
            email="test3@test.com",
            mobile="05055544333",
            date_of_birth="2000-12-12"
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(body=body, contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)



    async def test_get_contacts_birthdays(self):
        today = datetime.now().date()
        contacts = [
            Contact(date_of_birth=(today + timedelta(days=7))),
            Contact(date_of_birth=(today + timedelta(days=7))),
            Contact(date_of_birth=(today + timedelta(days=7))),
        ]

        self.session.execute.return_value.fetchall.return_value = contacts
        result = await get_contacts_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, contacts)



    async def test_contacts_by(self):
        contact1 = Contact(name="Stepan", surname="Bandera", email="bandera@test.com", user=self.user)
        contact2 = Contact(name="Dmytro", surname="Yarosh", email="yarosh@test.com", user=self.user)
        contact3 = Contact(name="Roman", surname="Shuhevych", email="shuhevych@test.com", user=self.user)


        mock_query = MagicMock()

        with patch.object(self.session, 'query', return_value=mock_query):
            mock_query.filter.return_value = mock_query
            mock_query.filter_by.return_value = mock_query

            mock_query.all.return_value = [contact1]
            result = await get_contacts_by(name="", surname ="Bandera", email="", user=self.user,
                                               db=self.session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "Stepan")
            self.assertEqual(result[0].surname, "Bandera")
            self.assertEqual(result[0].email, "bandera@test.com")


            mock_query.all.return_value = [contact2]
            result = await get_contacts_by(name="Dmytro", surname="", email="", user=self.user,
                                               db=self.session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "Dmytro")
            self.assertEqual(result[0].surname, "Yarosh")
            self.assertEqual(result[0].email, "yarosh@test.com")


            mock_query.all.return_value = [contact3]
            result = await get_contacts_by(name="", surname="", email="shuhevych@test.com", user=self.user,
                                               db=self.session)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].name, "Roman")
            self.assertEqual(result[0].surname, "Shuhevych")
            self.assertEqual(result[0].email, "shuhevych@test.com")


if __name__ == '__main__':
    unittest.main()
