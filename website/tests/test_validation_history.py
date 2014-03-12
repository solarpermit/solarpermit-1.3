from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from website.models import User, RatingCategory, ActionCategory, Jurisdiction, Question, AnswerReference
from django.contrib.auth import authenticate
from django.conf import settings
import json
client = Client()
class TestValidHistory(TestCase):
    def setUp(self):
#create a local users object for testuser1, 2, 3, out of a list build using the Django users model
        qName = ["approved with downvotes",
                 "approved without downvotes",
                 "approved with no votes",
                 "approved multi value with downvotes",
                 "approved multi value without downvotes",
                 "rejected with downvotes",
                 "rejected with downvotes and upvotes",
                 "rejected multi value with downvotes",
                 "rejected multi value with downvotes and upvotes",
                 "approved by superuser"
                 ]
        self.users = [User.objects.create_user("testuser%s" % id, 
                                               "testuser%s@testing.solarpermit.org" % id,
                                                "testuser")
                          for id in xrange(3)]

        RatingCategory.objects.create(name='Points',
                                      description='Number of points',
                                      rating_type='N').save()

        ActionCategory.objects.create(name='VoteRequirement',
                                      description='Vote on Requirement',
                                      rating_category_id=1,
                                      points=2).save()

        self.ahj = Jurisdiction.objects.create(city = "foo city",
                                                name_for_url = "foo1",
                                                description = "foo",
                                                state = "CA",
                                                jurisdiction_type = "CI",
                                                name = "foo")

        self.questions = [Question.objects.create(label="test %s" % name, question="test%s" % id)
                              for id in xrange(10) for name in qName]

        self.answers = [AnswerReference.objects
                                       .create(jurisdiction=self.ahj,
                                               question=question,
                                               value='test answer')
                             for question in self.questions]


    def test_validate(self):
        logged_in = client.login(username='testuser0',
                                 password='testuser')
        self.assertTrue(logged_in)
        down_votes = 0
        up_votes = 1
        direction = "up"
        (status, commands) = vote(client, self.ahj, self.answers[0], direction)
        self.assertEqual(status, 200)
        self.assertNotEqual(self.ahj.id,0)
        self.do_test_vote( client, self.ahj, self.answers[0], direction, up_votes, down_votes)

#      1  approved with downvotes
        # 3 upvotes, 2 down votes
#      2  approved without downvotes
        # 1 upvote
#      3  approved with no votes
        #no votes
#      4  approved multi value with downvotes
        #answer one: downvote, upvote 3
        #answer two: downvote 2
#      5  approved multi value without downvotes
        #answer one: upvote 3
        #answer two: downvote 2
#      6  rejected with downvotes
        #downvote 2
#      7  rejected with downvotes and upvotes
        #upvote 1 downvote 2
#      8  rejected multi value with downvotes
        #answer one downvote 2
        #answer two downvote 2
#      9  rejected multi value with downvotes and upvotes
        #answer one upvote 1 downvote 2
        #answer two upvote 1 downvote 2
#      10 approved by superuser
        #login as superuser. upvote? approve?
        
        #i altered do_test_vote to not include a test against the response for jurisdiction_id since it doesnt exist.
    def do_test_vote(self, client, ahj, answer, direction, up_votes, down_votes):
        (status, commands) = vote(client, ahj, answer, direction)
        self.assertEqual(status, 200)
        self.assertTrue(len(commands) >= 1)
        val = commands[0]["val"]
        self.assertIn(str(answer.id),
                      val["answers_votes"])
        self.assertEqual(up_votes,
                         val["answers_votes"][str(answer.id)]["total_up_votes"])
        self.assertEqual(down_votes,
                         val["answers_votes"][str(answer.id)]["total_down_votes"])

def vote(client, ahj, answer, direction):
    res = client.post('/jurisdiction/%s/' % ahj.name_for_url, #res is response of client
                      { 'ajax': 'vote', #send through ajax
                        'entity_id': answer.id, 
                        'entity_name': 'requirement',
                        'vote': direction, #direction up or down. 
                        'confirmed': '' })
    return (res.status_code, try_decode(res.content)) #return the status code, look for 200, then attempt to decode the content
def try_decode(content):
    try:
        return json.loads(content)
    except:
        return None
def dump(obj):
    for attr in dir(obj):
        if hasattr( obj, attr ):
            print( "obj.%s = %s" % (attr, getattr(obj, attr)))


'''
Will get 301 status code if no trailing slash is in place.
merge to devel update to fix issue #53
cron_validate_answers

function setup
Create sample jurisdiction
Create sample question for:
      1  approved with downvotes
      2  approved without downvotes
      3  approved with no votes
      4  approved multi value with downvotes
      5  approved multi value without downvotes
      6  rejected with downvotes
      7  rejected with downvotes and upvotes
      8  rejected multi value with downvotes
      9  rejected multi value with downvotes and upvotes
      10 approved by superuser

    create sample answers (multianswer questions will have 3 answers, pending, approved, reject)

function vote
    downvote answer to 2 to reject
    upvote answer to 1 to approve
    downvote answer, upvote to downvote + 1 to approve
    leave answer pending for week to approve

function timepass
    simulate days passing
    call cron script every simulated day.
    assert answered questions against template
    log errors
            self.users = [User.objects.create_user("testuser%s" % id, "testuser%s@testing.solarpermit.org" % id, "testuser") for id in xrange(3)]

'''        
#lss; at first it confused me that they used the for loops in this way.
# thought it would be no different than
# for ahj in self.ahj:
#    for question in self.questions:
#        self.answers = [AnswerReference.objects.create(jurisdiction=ahj, question=question, value='test answer')
# But it actually is, done the way above, it would create a new object for each answer and replace everything thats in there
# Idk if this is a python thing, but i really like it, going to remember it
# tried calling TestVoting.vote()... didnt work because i was calling the class test vote, and vote is not part of the class test vote
# the following is a successful vote, sent to the sample jur in FL. was able to upvote the permiting department name
# first I need to have the django client
# from django.test.client import Client
# c = Client()
# Then i need to make a user, (This made an actual user on the site, not just a test user in a test env)
# User.objects.create_user("testuser00001", "testuser001@testing.solarpermit.org", "testuser")
# WARNING creating a user this way does not invoke UserDetail, and will not allow the user to login on an actual browser. good catch, user detail is need inorder to have a complete test me thinks
# Must be inside a class invoking TestCase in order to use a test env, then call the User to an new object exp: 
# self.user = User.objects.create_user("testuser00001", "testuser001@testing.solarpermit.org", "testuser") for one user, or inside [] for multi users
# to login with a user
# c.login(username='testuser001',password='testuser')
# should return True and user should be logged in
# test to make sure user is logged in: 
# logged_in = c.login(username='testuser00001',password-'testuser')
# self.assertTrue(logged_in)
# then you can vote using:
# res = c.post('/jurisdiction/sample-jurisdiction-fl/', {'ajax': 'vote','entity_id': '27431', 'entity_name': 'requirement','vote': 'up', 'confirmed':''})
# this posts to the login page over ajax, and then assigns the response to res.
# res is an object containing res.status_code and res.content
# on the site actual user creation is handled with jquery. static/skins/templates/solarpermit/website/accounts/create_account.js'''