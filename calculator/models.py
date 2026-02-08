# -*- coding: utf-8 -*-

from __future__ import annotations

from django.db import models
from django.contrib.auth.models import User


class YearStatistics(models.Model):
    year = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.CharField(max_length=500)
    detailed_report = models.TextField(blank=True, null=True)
    coef_modifier = models.FloatField()
    additional_coef = models.FloatField(default=0.0)

    STATUS_CHOICES = (
        (0, 'не подписан'),
        (1, 'подписан'),
        (2, 'одобрен ответственным по лаборатории'),
        (3, 'утвержден директором'),
    )

    STATUS_SHORT_CHOICES = (
        (0, 'не подп.'),
        (1, 'подписан'),
        (2, 'одобрен'),
        (3, 'утвержден'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES)
    calcasmaximum = models.BooleanField(default=False)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return f"{self.user.username}{self.year}"


class SelectedJournal(models.Model):
    fullname = models.CharField(max_length=500)

    TYPE_CHOICES = (
        ('A', 'список A'),
        ('B', 'список B'),
        ('P', 'издательство'),
    )

    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    impactfactor = models.FloatField(default=0.0, null=True, blank=True)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.fullname


class Cost(models.Model):
    value = models.IntegerField()
    note = models.CharField(max_length=500)

    class Meta:
        managed = False

    def __str__(self) -> str:
        return self.note


class Attribute(models.Model):
    user = models.OneToOneField(
        User,
        db_column="user_id",
        primary_key=True,
        on_delete=models.DO_NOTHING,
    )


    class Meta:
        managed = False
        db_table = "calculator_attribute"

    # rank of the person
    RANK_CHOICES = (
        ('N', 'нет'),
        ('M', 'м.н.с.'),
        ('H', 'н.с.'),
        ('S', 'с.н.с.'),
        ('V', 'в.н.с.'),
        ('G', 'г.н.с.'),
        ('U', 'ученый секретарь'),
        ('R', 'советник РАН'),
        ('A', 'зам. дир. по научной раб.'),
        ('Z', 'зав. лаб.'),
        ('B', 'директор ММИ'),
        ('D', 'директор ПОМИ'),
    )
    rank = models.CharField(max_length=1, choices=RANK_CHOICES)

    STATUS_CHOICES = (
        ('N', 'сотрудник'),
        ('S', 'аспирант'),
        ('K', 'по контракту'),
        ('D', 'докторант'),
        ('L', 'запись лаборатории'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    TITLE_CHOICES = (
        ('N', 'нет звания'),
        ('C', 'с.н.с.'),
        ('D', 'доцент'),
        ('P', 'профессор'),
        ('T', 'чл.-корр. РАН'),
        ('A', 'академик РАН'),
    )
    title = models.CharField(max_length=1, choices=TITLE_CHOICES)

    diplom_year = models.IntegerField(null=True, blank=True)
    phd_year = models.IntegerField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)

    DEGREE_CHOICES = (
        ('N', 'нет степени'),
        ('K', 'кандидат наук'),
        ('D', 'доктор наук'),
    )
    degree = models.CharField(max_length=1, choices=DEGREE_CHOICES)

    is_admin = models.BooleanField(default=False)
    is_zavlab = models.BooleanField(default=False)
    is_headlab = models.BooleanField(null=True, blank=True)
    is_laboratory = models.BooleanField(null=True, blank=True)
    is_institute = models.BooleanField(null=True, blank=True)

    rate_choices = (
        (0, 'полная'),
        (1, '0.9'),
        (2, '0.8'),
        (3, '0.75'),
        (4, '0.7'),
        (5, '0.6'),
        (6, '0.5'),
        (7, '0.4'),
        (8, '0.3'),
        (9, '0.25'),
        (10, '0.2'),
        (11, '0.1'),
        (12, '0.0'),
    )

    rate = models.IntegerField(choices=rate_choices)
    email_verbose = models.BooleanField(default=False)

    class Meta:
        managed = False
    def __str__(self) -> str:
        return self.user.username
