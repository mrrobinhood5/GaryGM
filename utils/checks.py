# TODO: Move the Owner ID to DB
def is_owner(ctx):
    return ctx.messsage.author.id == 623277032930803742


def is_valid_prefix(msg):
    print("valid prefix")
    return ':' in msg.content


