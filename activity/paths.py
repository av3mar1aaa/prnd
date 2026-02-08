from prnd.activity.acttypes import *

def get_back_act_path(act_type, userid):
  return type2name(act_type)+"/"+str(userid)+"/"

def get_new_act_path(act_type, userid):
  return type2name(act_type)+"/"+str(userid)+"/add/"

def get_modify_act_path(act_type, userid, act):
  return type2name(act_type)+"/"+str(userid)+"/"+str(act.id)+"/"

def get_delete_act_path(act_type, userid, act):
  return type2name(act_type)+"/"+str(userid)+"/"+str(act.id)+"/delete/"

def get_act_path(act_type, userid, act):
  return get_modify_act_path(act_type, userid, act)  
  
def get_user_profile_path(userid):
  return "profile/" + str(userid) + "/"

def get_user_report_path(userid, year):
  return "year_reports/" + str(userid) + "/" + str(year) + "/"

def get_user_attestation_path(userid):
  return "user_attestation/" + str(userid) + "/"
