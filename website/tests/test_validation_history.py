from django.utils import unittest, timezone
from unittest import TestCase
from django.test.client import Client
from website.models import User, RatingCategory, ActionCategory, Jurisdiction, Question, AnswerReference, QuestionCategory, Action
from django.contrib.auth import authenticate
from django.conf import settings
from datetime import timedelta, datetime, date
from django.conf import settings as django_settings
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
import mock
import json
client = Client()
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

#lss;
#given a time, run FieldValidationCycleUtil.cron_validate_answers using mock date
def mockCronValidate(futureTime):
    with mock.patch('website.utils.fieldValidationCycleUtil.date') as mock_date:#can we mock datetime as date? making fieldval think 
        mock_date.today.return_value = futureTime
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        valUtil = FieldValidationCycleUtil()
        valUtil.cron_validate_answers()
            
class TestValidHistory(TestCase):
    def setUp(self):
        
        self.users = [User.objects.create_user("testuser%s" % id, 
                                               "testuser%s@testing.solarpermit.org" % id,
                                                "testuser")
                          for id in xrange(10)]
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
        
        self.qCategory = QuestionCategory.objects.get(id = 1)
        
        self.questions = [Question.objects.create(label="test%s" % id, question="test%s" % id)
                              for id in xrange(10)]
        for x in xrange(10):
            self.questions[x].category = QuestionCategory.objects.get(id = 1)
            
        self.questionsMulti = [Question.objects.create(label="test%s" % id, question="test%s" % id, has_multivalues = True)
                              for id in xrange(4)]
        for x in xrange(4):
            self.questionsMulti[x].category = QuestionCategory.objects.get(id = 1)
        self.answers = [AnswerReference.objects
                                       .create(jurisdiction=self.ahj,
                                               question=question,
                                               value='test answer')
                             for question in self.questions]
        self.answersMulti = [AnswerReference.objects
                                       .create(jurisdiction=self.ahj,
                                               question=question,
                                               value='test answer multi')
                             for question in self.questionsMulti] 
        self.answersMulti.extend([AnswerReference.objects
                                       .create(jurisdiction=self.ahj,
                                               question=question,
                                               value='test answer multi 2')
                             for question in self.questionsMulti])

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

    def loginUser(self, user): #feed user number
        logged_in = client.login(username='testuser%s' % user,
                            password='testuser')
        self.assertTrue(logged_in)
    #lss;
    #asserts a particular approval status for an answer
    #accepts either an id, or a list of ids
    def assertApprovalStatus(self, answer_id, status):
        for ans_id in answer_id:
            ansId = self.answers[ans_id].id
            answer = AnswerReference.objects.get(id = ansId)
            answer_status = answer.approval_status
            self.assertEqual(str(answer_status), status)
                
    def pushVote(self,votes,currentOpp,lastUser,answerNum,multi,direction): #number of times to upvote, current amount of down votes, last test user we used, current test number (answer ref), multi is a boolean depicting if we use answers or answersmulti 
        userNum = lastUser + 1
        inc = 0
        currentUsed = 0 #current amount of votes in our suggested direction
        self.loginUser(userNum) 
        while inc < votes: # while our incrementor is less than our total upvotes,
            if currentUsed <= votes: # if our current amount of upvotes is less or equal to our max upvote
                currentUsed = currentUsed + 1 #inc current upvotes
            if direction == "up":
                if multi == False:
                    self.do_test_vote( client, self.ahj, self.answers[answerNum], direction, currentUsed, currentOpp)
                else:
                    self.do_test_vote( client, self.ahj, self.answersMulti[answerNum], direction, currentUsed, currentOpp)
            elif direction == "down":
                if multi == False:
                    self.do_test_vote( client, self.ahj, self.answers[answerNum], direction, currentOpp, currentUsed)
                else:
                    self.do_test_vote( client, self.ahj, self.answersMulti[answerNum], direction, currentOpp, currentUsed)
            userNum = userNum + 1
            self.loginUser(userNum)
            inc = inc + 1
        inc = 0 # null out incs
        
    def test_Valid_Vote(self):
        #save all answers to database
        #make sure all answers are pending
        pendingList = xrange(18)        
        self.assertApprovalStatus(pendingList,'P')
        #run test to make sure that all approval status = P
#      test #0 answer#0 Goal: approved with downvotes
        # 3 upvotes, 1 down votes        
        self.pushVote(1, 0, 0, 0,False,"down")
        self.pushVote(3, 1, 1, 0,False,"up")
#      test #1 answer#1  goal approved without downvotes 
        # 3 upvote
        #self.pushVote(3, 0, 0, 1, False,"up")
#     test #2 answer#2 goal: approved with no votes #over time
        #no votes
        #####just a note that answer 2 lives here 
#      test #3 answer#3  rejected with downvotes
        #downvote 2
        self.pushVote(2, 0, 0, 3, False,"down")
#      test #4 answer#4  rejected with downvotes and upvotes
        #upvote 1 downvote 2
        self.pushVote(1, 0, 0, 4, False,"up")
        self.pushVote(2, 1, 1, 4, False,"down")
#      Test #5 answerMulti#0 & 4  approved multi value with downvotes
        # Test#5 #answer 0: downvote 2
        self.pushVote(2, 0, 0, 0, True,"down")
        # Test#5 #answer 1: downvote 1, upvote 3
        self.pushVote(1, 0, 0, 4, True,"down")
        self.pushVote(3, 1, 1, 4, True,"up")
#      test# 6 answerMulti# 1 & 5 approved multi values, one with upvotes, one without, both without downvotes
        #answer 1: upvote 3
        self.pushVote(3, 0, 0, 1, True,"up")
        #answer 5: no votes        
#      test# 7  answerMulti# 2 & 6 rejected multi value with downvotes
        #answer 2 downvote 2
        self.pushVote(2, 0, 0, 2, True,"down")
        #answer 6 downvote 2
        self.pushVote(2, 0, 0, 6, True,"down")
#      test# 8 answerMulti# 3 & 7  rejected multi value with downvotes and upvotes
        #answer 3 upvote 1 downvote 2
        self.pushVote(1, 0, 0, 3, True,"up")
        self.pushVote(2, 1, 1, 3, True,"down")
        #answer 7 upvote 1 downvote 2
        self.pushVote(1, 0, 0, 7, True,"up")
        self.pushVote(2, 1, 1, 7, True,"down")
        
        for answer in self.answers:
            answer.save(force_update=True)
        for answer in self.answersMulti:
            answer.save(force_update=True)
        for question in self.questions:
            question.save(force_update=True)
        for question in self.questionsMulti:
            question.save(force_update=True)

        testTime = date(int(timezone.now().year),int(timezone.now().month),int(timezone.now().day))
        daysPass = django_settings.NUM_DAYS_UNCHALLENGED_B4_APPROVED + 1
        diff = timedelta(days=daysPass)
        futureTime = testTime + diff #todays date plus 7 days                
        
        
        
        #insufficient timedelta
        mockCronValidate(testTime + timedelta(days=django_settings.NUM_DAYS_UNCHALLENGED_B4_APPROVED - 1))
        pendingList = xrange(18)             
        self.assertApprovalStatus(pendingList, 'P')

        
        #sufficient timedelta
        mockCronValidate(futureTime)        
        #import pdb
        #pdb.set_trace()
        approveList = [0,1, 2, 15, 12, 16] 
        rejectList = [3,4,11,13,17,14,18]
        self.assertApprovalStatus(approveList, 'A')
        self.assertApprovalStatus(rejectList, 'R')