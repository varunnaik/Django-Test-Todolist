from django.test import TestCase
from models import Item
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from tastypie_test import ResourceTestCase
import datetime

class ItemTest(TestCase):

    def setUp(self):
        # Create a test user for this test
        user = User()
        user.username = "user 1"
        user.save()
        self.user = user
        
        # Create a test item for this test
        item = Item()
        item.name = "test item"
        item.notes = "testing..."
        item.user = user
        item.save()
        self.item = item

    def test_todo_saved(self):
        """Test that the item was saved properly"""
        items = Item.objects.all()
        self.assertEquals(len(items), 1)
        
        item = items[0]
        self.assertEquals(item, self.item)
        
    def test_todo_defaults(self):
        """Are the default values filled in properly?"""
        self.assertEquals(self.item.priority, 0)
        self.assertEquals(self.item.due, None)
        self.assertEquals(self.item.done, False)
        self.assertEquals(self.item.user, self.user)
        
    def test_todo_editable(self):
        """Test that the todo item is editable"""
        self.item.name = "edited title"
        self.item.priority = 3
        self.item.save()
        
        items = Item.objects.all()
        self.assertEquals(len(items), 1)
        
        item = items[0]
        self.assertEquals(item.name, "edited title")
        self.assertEquals(item.priority, 3)
        self.assertEquals(item.notes, "testing...")
        
    def test_todo_deleteable(self):
        """Can we delete todo items?"""
        self.item.delete()
        items = Item.objects.all()
        self.assertEquals(len(items), 0)
        
    def test_todo_validated(self):
        """Test that the todo item is validated properly."""

    def test_todo_item(self):
        """Tests the todo item model"""
        # Does validation fail on an invalid item?
        item = Item()
        validatedSuccessfully = False
        try:
            item.full_clean()
        except ValidationError:
            validatedSuccessfully = True
            
        self.assertEquals(validatedSuccessfully, True)
        
        # Does validation pass on a valid item?
        item.name = "test"
        item.user = self.user
        validatedSuccessfully = True
        try:
            item.full_clean()
        except ValidationError:
            validatedSuccessfully = False
            
        self.assertEquals(validatedSuccessfully, True)
        


class ItemApiTest(ResourceTestCase):
    """Tests for the todo list API"""

    def setUp(self):
        super(ItemApiTest, self).setUp()

        # Create a user.
        self.username = 'test_user'
        self.password = 'test_pass'
        self.user = User.objects.create_user(self.username, 'test_user@example.com', self.password)
        
        # Create another user
        self.username2 = 'test_user2'
        self.password2 = 'test_pass2'
        self.user2 = User.objects.create_user(self.username2, 'test_user2@example.com', self.password2)

        item = Item()
        item.name = "Test Item #1"
        item.user = self.user
        item.notes = "testing..."
        item.save()
        self.item = item

        # Build a URI for the item
        self.detail_uri = '/api/v1/todo/{0}/'.format(self.item.pk)
        
        # ...as well as a URI to list all items
        self.list_uri = '/api/v1/todo/'

        # ...and URIs for each user
        self.user_uri = '/api/v1/user/{0}/'.format(self.user.pk)
        self.user2_uri = '/api/v1/user/{0}/'.format(self.user2.pk)

        # The data we'll send on POST requests.
        self.post_data = {
            'user': self.user_uri,
            'name': 'Test Item #2'
        }
        
        self.post_data2 = {
            'user': self.user2_uri,
            'name': 'Test Item #3'
        }
        

        # Expected test item JSON from server
        self.test_item_json = {
            'name': 'Test Item #1',
            'created': str(self.item.created),
            'notes': 'testing...',
            'due': None,
            'priority': 0,
            'done': False,
            'user': self.user_uri,
            'id': str(self.item.pk),
            'resource_uri': self.detail_uri 
        }
            
    def get_credentials(self):
        """Helper to create HTTP Basic auth credentials"""
        return self.create_basic(username=self.username, password=self.password)
        
    def test_get_list_unauthorzied(self):
        """Ensure we get HTTP 401 for unauthorised requests"""
        self.assertHttpUnauthorized(self.api_client.get(self.list_uri, format='json'))
        
    def test_get_list_json(self):
        """Test that we can list access our items properly when authorised"""
        resp = self.api_client.get(self.list_uri, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)

        # Ensure we got only one item.
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        
        # And ensure that the item is correct.
        self.assertEqual(self.deserialize(resp)['objects'][0], self.test_item_json)
        
    def test_get_detail_unauthenticated(self):
        """Get single item, unauthenticated"""
        self.assertHttpUnauthorized(self.api_client.get(self.detail_uri, format='json'))
        
    def test_get_detail_json(self):
        """Get single item, authenticated"""
        resp = self.api_client.get(self.detail_uri, format='json', authentication=self.get_credentials())
        self.assertValidJSONResponse(resp)
        self.assertKeys(self.deserialize(resp), self.test_item_json)
        
    def test_post_list_unauthenticated(self):
        """Post single item, unauthenticated"""
        self.assertHttpUnauthorized(self.api_client.post(self.list_uri, format='json', data=self.test_item_json))

    def test_post_list(self):
        """Post a single item, authenticated"""
        # Ensure there is only one item
        self.assertEqual(Item.objects.count(), 1)
        self.assertHttpCreated(self.api_client.post(self.list_uri, format='json', data=self.post_data, authentication=self.get_credentials()))
        # Verify a new item has been added.
        self.assertEqual(Item.objects.count(), 2)
        self.assertEqual(len(Item.objects.filter(name__exact='Test Item #2')),1)
        
    def test_create_another_user_item(self):
        """As one user, try creating an item for another user and ensure it fails"""
        self.assertEqual(Item.objects.count(), 1)
        # As user 1, create a todo item for user 2
        self.assertHttpBadRequest(self.api_client.post(self.list_uri, format='json', data=self.post_data2, authentication=self.get_credentials()))
        
    def test_put_detail_unauthenticated(self):
        """Put an item, unauthenticated"""
        self.assertHttpUnauthorized(self.api_client.put(self.detail_uri, format='json', data=self.post_data))

    def test_put_detail(self):
        """Put an item, authenticated"""
        original_pk = self.item.pk
        # Grab the current data & modify it slightly.
        original_data = self.deserialize(self.api_client.get(self.detail_uri, format='json', authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data['name'] = 'Updated: Test Item #1'
        new_data['created'] = '2012-07-09'

        self.assertEqual(Item.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.put(self.detail_uri, format='json', data=new_data, authentication=self.get_credentials()))
        # Make sure the count hasn't changed & we did an update.
        self.assertEqual(Item.objects.count(), 1)
        # Check for updated data.
        self.assertEqual(Item.objects.get(pk=original_pk).name, 'Updated: Test Item #1')
        self.assertEqual(Item.objects.get(pk=original_pk).notes, 'testing...')
        self.assertEqual(Item.objects.get(pk=original_pk).created, datetime.date(2012, 7, 9))
        
    def test_put_user_fails(self):
        """Attempting to change the user with a PUT request should fail"""
        original_pk = self.item.pk
        # Grab the current data & modify it slightly.
        original_data = self.deserialize(self.api_client.get(self.detail_uri, format='json', authentication=self.get_credentials()))
        new_data = original_data.copy()
        new_data['user'] = self.user2_uri
        
        self.assertHttpBadRequest(self.api_client.put(self.detail_uri, format='json', data=new_data, authentication=self.get_credentials()))

    def test_delete_detail_unauthenticated(self):
        """Delete an item, unauthenticated"""
        self.assertHttpUnauthorized(self.api_client.delete(self.detail_uri, format='json'))

    def test_delete_detail(self):
        """Delete an item, authenticated"""
        self.assertEqual(Item.objects.count(), 1)
        self.assertHttpAccepted(self.api_client.delete(self.detail_uri, format='json', authentication=self.get_credentials()))
        self.assertEqual(Item.objects.count(), 0)
        
    def test_delete_list(self):
        """Ensure delete fails on the list URI"""
        self.assertHttpMethodNotAllowed(self.api_client.delete(self.list_uri, format='json', authentication=self.get_credentials()))
        
    def test_post_detail(self):
        """Ensure post fails on the detail URI"""
        self.assertHttpMethodNotAllowed(self.api_client.post(self.detail_uri, format='json', data=self.post_data, authentication=self.get_credentials()))
        
""" NOTES:
    For manual testing, use curl as follows:
    
    curl --dump-header - --user test:test http://localhost:8000/api/v1/todo/
    -X POST --data '{"user": "/api/v1/user/2/", "name": "Test Item #3", "prio
    rity": "3", "due": "2012-08-10", "notes": "nothing, really"}' -H "Content-Type: applic
    ation/json"
    
    where test:test is the username and password of the user, and /todo/api/v1/user/2/ is the URI of the user in the todo list app.
"""