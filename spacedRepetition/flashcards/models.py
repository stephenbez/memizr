from django.db import models
from datetime import date
import random

def get_days_so_far():
    return (date.today() - date(2010,10,18)).days

class Card(models.Model):
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=200)
    grade = models.IntegerField(null=True, blank=True)    
    current_interval = models.IntegerField(default=0)
    easiness = models.FloatField(default=2.5)
    next_rep_day = models.IntegerField(default=0)
    retention_reps_since_lapse = models.IntegerField(default=0)

    def __unicode__(self):
        return "Q: %s, A: %s, Grade %s, current_interval %i, easiness %f, next_rep_day %i" % \
            (self.question, self.answer, self.grade, self.current_interval, self.easiness, self.next_rep_day)

    def process_answer(self, new_grade):
        if self.grade == None:
            interval = self.__calculate_initial_interval(new_grade)
        else:
            interval = self.__get_new_interval(new_grade)
        
        interval += self.__calculate_interval_noise(interval)
        
        self.current_interval = interval
        self.next_rep_day = get_days_so_far() + interval
        self.grade = new_grade

    def __get_new_interval(self, new_grade):
        if self.grade in [0,1] and new_grade in [0, 1]:
            return 0
        elif self.grade in [0,1] and new_grade in [2,3,4,5]:
            return 1
        elif self.grade in [2,3,4,5] and new_grade in [0,1]:
            self.retention_reps_since_lapse = 0
            return 1
        elif self.grade in [2,3,4,5] and new_grade in [2,3,4,5]:
            self.retention_reps_since_lapse += 1
            return self.__get_interval_for_remember_both_times(new_grade)
        raise Exception("Invalid grade combination")

    def __get_interval_for_remember_both_times(self, new_grade):
        self.__adjust_easiness(new_grade)
        if self.retention_reps_since_lapse == 1:
            return 6
        elif new_grade in [2, 3]:
            return self.current_interval
        elif new_grade in [4, 5]:
            return self.current_interval * self.easiness
        raise Exception("Invalid new_grade")

    def __adjust_easiness(self, new_grade):
        if new_grade == 2:
            self.easiness -= 0.16
        elif new_grade == 3:
            self.easiness -= 0.14
        elif new_grade == 5:
            self.easiness += 0.10
        
        if self.easiness < 1.3:
            self.easiness = 1.3
            
    def __calculate_interval_noise(self, interval):
        if interval == 0:
            return 0
        elif interval == 1:
            return random.randint(0,1)
        elif interval <= 10:
            return random.randint(-1,1)
        elif interval <= 60:
            return random.randint(-3,3)
        else:
            a = .05 * interval
            return round(random.uniform(-a,a))
        
    def __calculate_initial_interval(self, grade):
        interval = (0, 0, 1, 3, 4, 5) [grade]
        return interval
