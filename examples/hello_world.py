
def plugin(kernel, lifecycle):
    if lifecycle == 'register':
        @kernel.console_command('example', help="Says Hello World.")
        def example_cmd(channel, _, **kwargs):
            channel(_('Hello World'))


if __name__ == '__main__':
    import kernel
    k = kernel.Kernel("HelloWorld", version="0", profile="Hello World")
    k.add_plugin(plugin)
    k(partial=True)
    k.console("channel print console\n")
    k.console("example\n")
    k.console("help timer\n")
    k.console(".timer 1 1 quit\n")

