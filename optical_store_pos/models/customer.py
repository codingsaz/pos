class Customer:
    def __init__(self, id, name, phone, email):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email

    def __repr__(self):
        return f"Customer({self.id}, '{self.name}', '{self.phone}', '{self.email}')"
