# -*- coding: utf-8 -*-

from __future__ import annotations

from django.db import models
from django.contrib.auth.models import User

PUBLICATION_TYPES = (
    (0, 'journal'),
    (1, 'proceedings'),
    (2, 'preprint'),
)

LANGUAGE_TYPES = (
    (0, 'russian'),
    (1, 'foreign'),
)


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    authors = models.CharField(max_length=500)
    authornum = models.IntegerField()
    name = models.CharField(max_length=500)
    journal_id = models.IntegerField()
    journal = models.CharField(max_length=500)
    volume = models.CharField(max_length=500)
    jnumber = models.CharField(max_length=500)
    pages = models.CharField(max_length=500)
    year = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    webpage = models.CharField(max_length=500)
    idnumber = models.CharField(max_length=500)
    pubtype = models.IntegerField(choices=PUBLICATION_TYPES)
    language = models.IntegerField(choices=LANGUAGE_TYPES)
    instcoauthors = models.BooleanField(default=False)

    class Meta:
        managed = False

    def class_name(self):
        return 'Activity'

    def __str__(self) -> str:
        return self.name


CONFERENCE_TALK_TYPES = (
    (0, 'simple russian'),
    (1, 'simple international'),
    (2, 'invited russian'),
    (3, 'invited international'),
    (4, 'pdmi seminar'),
    (5, 'math community seminar'),
)


class Conference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    place = models.CharField(max_length=500)
    dates = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    authornum = models.IntegerField()
    talktitle = models.CharField(max_length=500)
    year = models.CharField(max_length=500)
    conftype = models.IntegerField(choices=CONFERENCE_TALK_TYPES)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.name


class Patent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    number = models.CharField(max_length=500)
    place = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    authornum = models.IntegerField()
    year = models.CharField(max_length=500)
    note = models.CharField(max_length=500)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.name


MONOGRAPH_GRIF_TYPES = (
    (0, 'no'),
    (1, 'yes'),
)


class Monograph(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    authors = models.CharField(max_length=500)
    journal = models.CharField(max_length=500)
    journal_id = models.IntegerField()
    authornum = models.IntegerField()
    pagenum = models.IntegerField()
    isbn = models.CharField(max_length=500)
    grif = models.IntegerField(choices=MONOGRAPH_GRIF_TYPES)
    year = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    coef = models.FloatField(default=2.0)

    class Meta:
        managed = False

    def class_name(self):
        return 'Monograph'

    def __str__(self) -> str:
        return self.name


COURSE_TYPES = (
    (0, 'first year'),
    (1, 'second year'),
    (2, 'more'),
    (3, 'studseminar'),
)

COURSE_DURATION_TYPES = (
    (0, 'one semester'),
    (1, 'two semesters'),
)


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)
    coursetype = models.IntegerField(choices=COURSE_TYPES)
    duration = models.IntegerField(choices=COURSE_DURATION_TYPES)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.name


SUPERVISING_TYPES = (
    (0, 'PhD'),
    (1, 'MSc'),
    (2, 'consult'),
)


class Supervising(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    institute = models.CharField(max_length=500)
    subject = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)
    suptype = models.IntegerField(choices=SUPERVISING_TYPES)
    further_affiliation = models.CharField(max_length=500)
    authornum = models.IntegerField()

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.name


ORGWORK_TYPES = (
    (0, 'russian conference'),
    (1, 'international conference'),
)


class OrgWork(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    place = models.CharField(max_length=500)
    dates = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)
    worktype = models.IntegerField(choices=ORGWORK_TYPES)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.name


OPPOSING_TYPES = (
    (0, 'kandidat'),
    (1, 'doktor'),
    (2, 'vedkandidat'),
    (3, 'veddoktor'),
)


class Opposing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    institute = models.CharField(max_length=500)
    subject = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)
    opptype = models.IntegerField(choices=OPPOSING_TYPES)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.name


class StudentSupervising(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.name


EDITING_TYPES = (
    (0, 'book'),
    (1, 'volume'),
    (2, 'proceedings'),
)


class Editing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    volume = models.CharField(max_length=500)
    journal = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)
    editingtype = models.IntegerField(choices=EDITING_TYPES)

    class Meta:
        managed = False

    def class_name(self):
        return 'Editing'

    def __str__(self) -> str:
        return self.name


class EditingCollegium(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    journal_id = models.IntegerField()
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)

    class Meta:
        managed = False

    def class_name(self):
        return 'EditingCollegium'

    def __str__(self) -> str:
        return ''


class Grant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    role = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)

    class Meta:
        managed = False

    def class_name(self):
        return 'Grant'

    def __str__(self) -> str:
        return self.name


class Award(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=500)
    note = models.CharField(max_length=500)
    year = models.CharField(max_length=500)

    class Meta:
        managed = False

    def class_name(self):
        return 'Award'

    def __str__(self) -> str:
        return self.name


class IndividualCoefficient(models.Model):
    coef = models.FloatField(default=1.0)
    coef_set_by_admin = models.FloatField(default=1.0)
    coef_set_by_zavlab = models.FloatField(default=1.0)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return f"{self.coef}"
