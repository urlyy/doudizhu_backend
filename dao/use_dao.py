from PO.user import User


# user1 = User(username="陈柱潜",password="1234", coin=100, rank=150, avatar="http://localhost:8000/static/96126bfd-f184-4816-86a1-db54b884b000.png")
# user2 = User(username="czq", password="1234",coin=100, rank=150, avatar="http://localhost:8000/static/96126bfd-f184-4816-86a1-db54b884b000.png")
# user3 = User(username="竹签陈", password="1234",coin=100, rank=150, avatar="http://localhost:8000/static/96126bfd-f184-4816-86a1-db54b884b000.png")
# user1.save()
# user2.save()
# user3.save()

u:User = User.select().where(User.username == 'czq').first()
print(u)
