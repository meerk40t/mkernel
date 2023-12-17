from kernel import Kernel


def bootstrap(profile="TestingDevice"):
    kernel = Kernel("TestDevice", version="0", profile="TestDevice", ignore_settings=True)
    kernel(partial=True)
    kernel.console("channel print console\n")
    return kernel
