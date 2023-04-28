MANAGE_SERVER=128
MANAGE_USER=64
MANAGE_CHANNEL=32
MANAGE_MESSAGES=16
ADD_REACTIONS=8
SEND_FILES=4
CHANGE_NICKNAME=2
SEND_MESSAGES=1

BASIC = ADD_REACTIONS + SEND_FILES + CHANGE_NICKNAME + SEND_MESSAGES
ADMIN = MANAGE_MESSAGES + MANAGE_CHANNEL + MANAGE_USER + MANAGE_SERVER + BASIC

def calculate_perms(srv, uid):
    roles = []
    for role in srv['members'][uid]['roles']:
        roles.append(srv['roles'][role])
    cap = 1
    for role in roles:
        if role['permissions'] >= cap:
            cap |= role['permissions']
    return cap

def has_perm(perm, perm_n):
    return perm & perm_n == perm_n