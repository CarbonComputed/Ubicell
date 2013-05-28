from models.Club import *
from models.User import *
from models.School import *
from models.University import *
from models.Post import *
from models.ProfileImage import * 
from models.Reply import *
import logging
from util import *

logger = logging.getLogger(__name__)



def make_club(ownerid,name,university,about="",members=[],admins=[],private=True,callback=None):
    if len(name) <= 0:
        return 500
    admins = admins
    logger.debug("Name "+ name)
    logger.debug("Admins " + str(admins))
    logger.debug("Members " + str(members))
    if ownerid not in admins:
        admins.append(ownerid)
    if ownerid not in members:
        members.append(ownerid)
    club = Club(Admins=admins,Members=members,About=about,Name=name,University=university,Private=private)
    club.save()
    for userid in members:
        user = User.objects(id=userid).first()
        subc = SubClub(Id=club.id,Name=name)
        user.Clubs.append(subc)
        user.save()
    if callback != None:
        return callback(200)
    return 200


def get_club(clubid,callback=None):
    club = Club.objects(id=clubid).first()
    if callback != None:
        return callback(club)
    return club
    

def del_club(clubid):
    pass

def confirm_member(uid,clubid,userid,callback=None):
    club = Club.objects(id=clubid).first()
    uid = ObjectId(uid)
    userid = ObjectId(userid)
    if uid not in club.Admins:
        if callback != None:
            return callback(500)
        return 500
    if userid in club.MemberRequests:
        club.MemberRequests.remove(userid)
        club.Members.append(userid)
        club.save()
        user = User.objects(id=userid).first()
        subc = SubClub(Id=club.id,Name=club.Name)
        user.Clubs.append(subc)
        user.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def add_member(clubid,userid,callback=None):

    club = Club.objects(id=clubid).first()
    if userid not in club.Members:
        if club.Private:
            club.MemberRequests.append(userid)
            club.save()
        else:
            club.Members.append(userid)
            club.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def del_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid in club.Members:
        club.Members.remove(userid)
        club.save()       
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def ban_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid not in club.BanList:
        club.BanList.append(userid)
        club.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def get_feed(clubid):
    club = Club.objects(id=clubid).first()
    if callback != None:
        return callback(club.Wall)
    return club.Wall

def get_members(clubid):
    club = Club.objects(id=clubid).first()
    if callback != None:
        return callback(club.Members)
    return club.Members

def promote_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid not in club.Admins:
        club.Admins.append(userid)
        club.save()
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200

def demote_member(clubid,userid):
    club = Club.objects(id=clubid).first()
    if userid in club.Admins:
        club.Admins.remove(userid)
        club.save()       
    else:
        if callback != None:
            return callback(500)
        return 500
    if callback != None:
        return callback(200)
        return 200






def get_member_data(clubid,callback=None):
    logger.info("Getting Club Members")
    members = Club.objects(id=clubid).first().Members
    print members
    coll = User._get_collection()
    members = coll.find({'Clubs.Id' : ObjectId(clubid)})
    # print members[0]['FirstName']
    if callback != None:
        return callback(members)
    return members

def get_member_req_data(clubid,callback=None):
    logger.info("Getting Club MemberRequests")
    member_reqs = Club.objects(id=clubid).first().MemberRequests
    print member_reqs
    coll = User._get_collection()
    member_reqs = coll.find({'_id' : {'$in' : member_reqs}})
    if callback != None:
        return callback(member_reqs)
    return member_reqs


