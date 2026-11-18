def get_responder(request):
    user = request.user
    # 用户没有部门，直接返回None，自动通过
    if not user.department:
        return None
    dept = user.department
    # 部门没有leader
    if not dept.leader:
        return None

    if dept.leader.uid == user.uid:
        if dept.name == '董事会':
            responder = None
        else:
            responder = dept.manager
    else:
        responder = dept.leader
    return responder
