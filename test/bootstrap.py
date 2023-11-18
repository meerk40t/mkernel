from kernel import Kernel


def bootstrap(profile="TestingDevice"):
    kernel = Kernel("TestDevice", version="0", profile="TestDevice")
    kernel()
    kernel.console("channel print console\n")
    return kernel
