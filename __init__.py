import CustomProperties
def initialize(context):
    # import lazily and defer initialization to the module
    CustomProperties.initialize(context)
