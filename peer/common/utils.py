def random_name():
    return str(__import__('uuid').uuid4())
