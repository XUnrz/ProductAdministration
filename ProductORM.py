from extension import db

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    # 商品数量
    quantity = db.Column(db.Integer, nullable=False)
    # 进货价
    price1 = db.Column(db.Float, nullable=False)
    # 零售价
    price2 = db.Column(db.Float, nullable=False)
    # vip价
    price3 = db.Column(db.Float, nullable=False)
    # 市代价
    price4 = db.Column(db.Float, nullable=False)
    # 省代价
    price5 = db.Column(db.Float, nullable=False)
    # 总代价
    price6 = db.Column(db.Float, nullable=False)

    def __init__(self, name, quantity, price1, price2, price3, price4, price5, price6):
        self.name = name
        self.quantity = quantity
        self.price1 = price1
        self.price2 = price2
        self.price3 = price3
        self.price4 = price4
        self.price5 = price5
        self.price6 = price6

    def save(self):
        db.session.add(self)
        db.session.commit()
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

