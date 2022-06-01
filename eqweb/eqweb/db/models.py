#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Jorge Morgado <jorge (at) morgado (dot) ch>
# Copyright (c)2016
#

from werkzeug import generate_password_hash, check_password_hash

# This is a circular import :-/
from eqweb.db.db import db

class User(db.Model):
    """ CREATE TABLE `event`.`user` (
            `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
            `name` VARCHAR(45) NOT NULL,
            `username` VARCHAR(45) NOT NULL,
            `password` VARCHAR(255) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `idx_username` (`username`),
            UNIQUE KEY `idx_search` (`username`, `password`)
        ) ENGINE=InnoDB;
    """
    __tablename__ = 'user'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(45), nullable=False)
    username = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    queries  = db.relationship('Query', primaryjoin='User.id==Query.userid')

    def __init__(self, name=None, username=None, password=None):
        self.name = name
        self.username = username
        self.set_password(password)

    def __repr__(self):
        return "<%s(name='%r', username='%r', password='%r')>" % \
            (self.__class__.__name__, self.name, self.username, self.password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Query(db.Model):
    """ CREATE TABLE `event`.`query` (
            `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
            `userid` INT(11) UNSIGNED NOT NULL,
            `desc` VARCHAR(45) NOT NULL,
            `request` VARCHAR(1024) NOT NULL,
            PRIMARY KEY (`id`),
            UNIQUE KEY `idx_userid_desc` (`userid`, `desc`),
            INDEX `idx_desc` (`desc`),
            CONSTRAINT FOREIGN KEY (`userid`) REFERENCES `user`(`id`)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        ) ENGINE=InnoDB;
    """
    __tablename__ = 'query'
    id      = db.Column(db.Integer, primary_key=True)
    userid  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    desc    = db.Column(db.String(45), nullable=False)
    request = db.Column(db.String(1024), nullable=False)

    def __init__(self, userid=None, desc=None, request=None):
        self.userid = userid
        self.desc = desc
        self.request = request

    def __repr__(self):
        return "<%s(userid=%lu, desc='%r', request='%r')>" % \
            (self.__class__.__name__, self.userid, self.desc, self.request)


class Queue(db.Model):
    """ CREATE TABLE `queue` (
          `id` INT(11) NOT NULL AUTO_INCREMENT,
          `ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          `source` VARCHAR(255) NOT NULL,
          `eventid` INT(11) NOT NULL DEFAULT '0',
          `lasteventid` INT(11) NOT NULL DEFAULT '0',
          `type` VARCHAR(255) NOT NULL,
          `state` VARCHAR(255) DEFAULT NULL,
          `statetype` VARCHAR(255) DEFAULT NULL,
          `laststate` VARCHAR(255) DEFAULT NULL,
          `count` INT(11) DEFAULT '1',
          `handled` TINYINT(1) NOT NULL DEFAULT '0',
          `ipv4` INT(10) unsigned DEFAULT NULL,
          `ipv6` binary(16) DEFAULT NULL,
          `hostname` VARCHAR(255) DEFAULT NULL,
          `servicename` VARCHAR(255) DEFAULT NULL,
          `date` VARCHAR(30) NOT NULL,
          `time` VARCHAR(30) NOT NULL,
          `message` TEXT,
          PRIMARY KEY (`id`),
          KEY `ts_idx` (`ts`),
          KEY `source_idx` (`source`),
          KEY `state_idx` (`state`(1)),
          KEY `handled_idx` (`handled`),
          KEY `ipv4_idx` (`ipv4`),
          KEY `ipv6_idx` (`ipv6`),
          KEY `hostname_idx` (`hostname`),
          KEY `eventid_idx` (`source`,`eventid`)
        ) ENGINE=InnoDB;
    """
    __tablename__ = 'queue'
    id          = db.Column(db.Integer, primary_key=True)
    ts          = db.Column(db.DateTime, nullable=False)
    source      = db.Column(db.String(255), nullable=False)
    eventid     = db.Column(db.Integer, nullable=False, default=0)
    lasteventid = db.Column(db.Integer, nullable=False, default=0)
    type        = db.Column(db.String(255), nullable=False)
    state       = db.Column(db.String(255), default=None)
    statetype   = db.Column(db.String(255), default=None)
    laststate   = db.Column(db.String(255), default=None)
    count       = db.Column(db.Integer, default=1)
    handled     = db.Column(db.Integer, nullable=False, default=0)
    ipv4        = db.Column(db.Integer, default=None)
    ipv6        = db.Column(db.Integer, default=None)
    hostname    = db.Column(db.String(255), default=None)
    servicename = db.Column(db.String(255), default=None)
    date        = db.Column(db.String(30), nullable=False)
    time        = db.Column(db.String(30), nullable=False)
    message     = db.Column(db.Text)

    def __repr__(self):
        return ("<%s(id=%d, ts=%r, source='%s', eventid=%lu, lasteventid=%lu, "
                "type='%s', state='%s', statetype='%s', laststate='%s', "
                "count=%lu, handled=%d, ipv4=%r, hostname='%s', "
                "servicename='%s', date='%s', time='%s', message='%r')>") % \
                (self.__class__.__name__, self.id, self.ts, self.source,
                self.eventid, self.lasteventid, self.type, self.state,
                self.statetype, self.laststate, self.count, self.handled,
                self.ipv4, self.hostname, self.servicename, self.date,
                self.time, self.message)
