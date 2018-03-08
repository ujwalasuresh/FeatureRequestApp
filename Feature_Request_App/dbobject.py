from models import RequestTicket, ClientName, ProductArea, Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func
from datetime import datetime

# db config
engine = create_engine('sqlite:///request_tickets.db')
#engine = create_engine('mysql://mysql:mysql@localhost/FeatureRequest')
session = sessionmaker()
session.configure(bind=engine)
s = session()


def create_tables():
    # table drop and creation
    #Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def get_all(user_id):
    # get all entries
    return s.query(RequestTicket)\
            .filter(RequestTicket.user_id == user_id)\
            .order_by(RequestTicket.client_priority).all()


def get_all_ticket_ids(user_id):
    """
    function gets all ids in RequestTicket table
    :return list of ids
    """
    id_list = []
    for id, in s.query(RequestTicket.id).filter(RequestTicket.user_id == user_id).all():
        id_list.append(id)
    return id_list


def insert_new(title, description, client, client_priority, target_date, url_root, product_area, user_id, ind=None):
    if ind is None:
        ind = 0
        try:
            ind = int(s.query(func.max(RequestTicket.id)).scalar()) +1
        except Exception as e:
            ind += 1
    # instantiate a new object from mapped class
    rt = RequestTicket(ind=int(ind), title=str(title), description=str(description), client=client,
                       client_priority=int(client_priority), target_date=datetime.strptime(target_date, "%a, %d %b %Y"),
                       ticket_url=url_root+'/ticket/'+str(ind), product_area=product_area, user_id=user_id)
    #print rt
    try:
        s.add(rt)
        s.commit()
    except Exception as e:
        s.rollback()
    # update the entry with ticket URL = "/ticket/" + entry.id


def check_priorities_EL(priority, user_id):
    """
    checks if there are any entries with equal of less priotiry
    :param priority:
    :return: list of id of the entries with equal or less priority
    """
    check = []
    for row in s.query(RequestTicket)\
                .filter(RequestTicket.user_id == user_id)\
                .filter(RequestTicket.client_priority >= priority).all():
        check.append(row.id)
    return check


def downgrade_priorities(entry_ids):
    """
    function requests entries with priorities and updating them assigning priotiries +1
    :param entry_ids:
    :return:
    """
    try:
        for idx in entry_ids:
            # got an entry by id
            entry = s.query(RequestTicket).filter(RequestTicket.id == idx).first()
            # assign entry's client_priority property
            p = int(entry.client_priority)
            # update the entry with incremented clients_priority
            s.query(RequestTicket).filter(RequestTicket.id == idx).update({"client_priority": p+1})
        s.commit()
    except Exception as e:
        s.rollback()


def get_possible_priorities(user_id):
    """
    :return: gathers all existing priorities and adds one more at the end
    """
    priority_list = []
    for p, in s.query(RequestTicket.client_priority)\
               .filter(RequestTicket.user_id == user_id).all():
        priority_list.append(p)
    # and the next one
    if len(priority_list) > 0:
        priority_list.append(priority_list[-1]+1)
    else:
        priority_list = [1]
    priority_list = set(priority_list)
    return list(priority_list)


def get_gaps(user_id):
    """
    :return: a list with gaps in priorities
    """
    priority_list = []
    for p, in s.query(RequestTicket.client_priority)\
               .filter(RequestTicket.user_id == user_id).all():
        priority_list.append(p)
    priority_gap_list = []
    max_p = 0
    try:
        max_p = max(priority_list)
    except Exception as e:
        max_p = 0
    for check_p in range(1, max_p+1):
        if check_p not in priority_list:
            priority_gap_list.append(check_p)
    return priority_gap_list


def eleminate_gaps(gap_list):
    """
    TODO: develop function to eleminate all gaps by updating priorities for existing entries
    :param gap_list:
    :return:
    """
    for g in sorted(gap_list, reversed):
        for priority in range(g+1, int(s.query(func.max(RequestTicket.client_priority)).scalar())+1):
            try:
                s.query(RequestTicket)\
                 .filter(RequestTicket.client_priority == priority)\
                 .update({"client_priority": priority-1})
                s.commit()
            except Exception as e:
                s.rollback()


def get_requests_by_id_list(id_list):
    """
    get a list of particular requests basing on a list of ids
    :param id_list:
    :return: list of requests
    """
    output = []
    for id in id_list:
        try:
            output.append(s.query(RequestTicket).filter(RequestTicket.id == id).first())
        except Exception as e:
            print "wrong list requested"
    return output


def get_client_list():
    """
    function to get all clients from db
    :return:
    """
    cn = ClientName()
    return cn.client_list()


def get_production_area_list():
    """
    function to get all clients from db
    :return:
    """
    pa=ProductArea()
    return pa.production_area_list()

def delete_entry(id):
    s.query(RequestTicket).filter(RequestTicket.id == id).delete()

def update_entry(ticket):
    rt = {'id': ticket['id'],
          'title': ticket['title'],
          'description': ticket['description'],
          'client': ticket['client'],
          'client_priority': ticket['client_priority'],
          'target_date': ticket['target_date'],
          'url_root': ticket['url_root'],
          'product_area': ticket['product_area']}
    s.query(RequestTicket).filter(RequestTicket.id == id).update({rt})

def register(username, email, password):
    print username
    print email
    print password
    usr = User(username=username, email=email, password=password)
    try:

        s.add(usr)

        s.commit()

        print "Successfully added"
        #print usr
    except Exception as e:
        print e
        s.rollback()

def login(username):
    try:
        print username
        get_user = s.query(User).filter(User.username == username).first()
        print "sss"
        return get_user, "Success"


    except Exception as e:
        print e
        #print "no such username"
        return "", "No such Username Registered"