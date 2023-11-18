# mkernel
The mkernel project (pronounced em-kernel) provides the extensible kernel used by the meerk40t project for any other projects. While developed with that in mind it was developed generically, and as such can be used for any project which may require any of the robust environmental features provided by the Kernel.

## Kernel
The Kernel class provides a suite of functionality. It serves as a central hub of communication between different plugins within the system.

Features include:
* Lifecycle based ecosystem of functionality.
* Job scheduler to provide repeated and time delineated function calls.
* OS independent context-path dependent persistent settings.
* Tree/Path `Context` to provide path-dependent views into the kernel.
* Internal console command system with easy registration of context based commands (Similar to Click).
* Command context pipelines for user executable modular data manipulation (Similar to Vpype).
* Centralized lookup for registered data across the program ecosystem.
* `service.providers` register a standard method for starting a particular service (if needed)
* `Service` provides direct reference-attributes to all contexts.
* `Service` provides methodology for swapping lookup data between different instances for the same service namespace.
* `lookup_listener` provide internal listening mechanisms for lookup changes.
* `signal()` provide efficient centralized communication for specifically flagged data. 
* `signal_listener` to register a function to be called by the signals.
* `Channel` to provide realtime lossless stream of data for debugging or utility that can be accessed by the user.
* `Modules` to provide reusable, registered classes, with properly bound lifecycles.
* plugin-based architecture to provide highly configurable plugin registration.
* lifecycle-aware plugins for `Modules` and `Services`.
* Manage lifecycle aware threads.
* Translation information and functionality.

# Lifecycle

There are three different lifecycle aware types within the ecosystem: `Modules`, `Services`, and `Kernel`.

Plugins are called for all events in an objects lifecycle (see methodology). The lifecycles events are called as specific functions on the lifecycle-aware objects themselves. A `Service` will be notified of `service_attach` by calling (if it exists) a `def service_attach()` function.

## Delegates
Lifecycle aware objects can also call `add_module_delegate()` for Modules or `add_service_delegate()` for Services. This will then not only call the lifecycle events on the primary object but also on all delegates of that object. Delegates will also have their `@signal_listener()` and `@lookup_listener()` on their functions automatically registered. 

## Plugin Configuration
The lifecycle events include a few pre-processing and configuration calls.

`plugins`: All plugins are first polled for plugins. This should, if it returns anything, return a set of other plugins.
`service`: Plugins are queried for `service` which should respond with the `provider` they are targeting. This service will be attached to the lifecycle of any and all services created from that provider.
`module`: Plugins are queried for `module` which should respond with the path of the module they are targeting. This plugin will be attached to instances of that module that are opened.
`invalidate`: Plugins are queried for `invalidate` which should return `True` if this plugin is invalid and should be removed from the list of plugins. 

## Kernel Lifecycle

By default, plugins are expected to be `kernel-plugins` and react to the lifecycle events of the kernel.
These are in order:
* `preregister`
* `register`: Most `register()` calls and establishment of different parts of the ecosystem should be done here.
* `configure`: Everything was registered but instances of other lifecycle objects are not started.
* `boot`: Most lifecycle objects are started.
* `postboot`
* `prestart`
* `start`
* `poststart`
* `ready`
* `finished`
* `premain`
* `mainloop`: The `console` or various gui mainloops will be executed here, they should capture the thread. 
* `postmain`: All the holds of the mainloop have been released.
* `preshutdown`: Everything should be unhooked and ready to be destroyed.
* `shutdown`: The kernel is terminating. You cannot count on anything still existing. Do housekeeping.

All registered plugins call `def plugin(kernel, lifecycle)` this is called with the kernel object and the current lifecycle. This is done for each lifecycle event. Plugins are required to use these to register and execute themselves at the appropriate times within the overall program's lifecycle. The primary reason for many of these events are that sometimes code execution requires that other registrations and code has executed before the code being provided. If they are registered at the correct lifecycle event, that guarantee is met. For example, if you need to execute a console command this should be done after `register` since all console commands should be registered during that lifecycle event.


```python 
def plugin(kernel, lifecycle):
    if lifecycle == 'register':
        @kernel.console_command('example', help="Says Hello World.")
        def example_cmd(command, channel, _, args=tuple(), **kwargs):
            channel(_('Hello World'))
```
In this example, we use the `kernel.console_command` to register a command called `"example"` which calls the channel with "Hello World" during the `register` lifecycle.
See: `examples/hello_world.py`

## Module Lifecycle

Modules are only expected to be started up and closed down. Their lifecycles are:
* `module_open`
* `module_clos`
* `shutdown`


# Scheduler

The scheduler is a thread which provides `Job` instances these can occur a number of times over a given duration. A scheduled job will skip run cycles if the job takes longer than the interval to complete. Refreshing guis and signals are processed through scheduled jobs.

The kernel scheduler is allowed for jobs to be scheduled. It launches a thread in the kernel which iterates through the different scheduled jobs, and running them when required. This thread is also used as during shutdown to terminate everything in a safe manner.

## Threads
Threads are registered in the kernel and executed normally. These are tracked and viewed with the `thread` channel for diagnostic purposes. And are required to complete for kernel shutdown. Starting a thread requires using the `threaded` command on the kernel or a context.

### Jobs
Jobs are either called within a context for `.add_job()` or a module can extend the Job and call `schedule()` and `unschedule()`.

## Timers
Timers are user set internal commands that execute repeatedly. These can be executed by the user in the console. This is an internal kernel command.
```
 help timer
     	timer.* <times:str> <duration:float>
     	(None) -> timer.* -> (None)
     	Argument: str 'times':
     		Number of times this timer should execute.
     	Argument: float 'duration':
     		How long in seconds between/before should this be run.
     	Option: bool ('--off', '-o'):
     		Turn this timer off
     	Option: bool ('--gui', '-g'):
     		Run this timer in the gui-thread
```

# Contexts
Contexts are the usual method of accessing data within the kernel. `kernel.get_context(<path>)` will give a context with that specific path set. This path is used as a namespace to allow multiple similar aspects. For example, if you had a `camera` plugin, it could register in `camera1`, `camera2`, `camera3` for identical but independent settings in the different namespaces.

Contexts also allow for simplified and shorthand commands compared to kernel. `context("help")` will call the help command in the console.

Signals, always provide `origin` as their first parameter. This is the context which issued the original signal.

# Persistent Settings.

The `Settings` uses python ConfigParser to write our persistent settings to disk. This is used by the Kernel to save any settings data on a context to disk during `shutdown`

The individual settings are usually initialized by calling `q = context.settings(<type>, <attr>, <default)`. If the setting was found in persistent settings then the persistent value will be used, else `context.<attr> = default` is set.

Persistent settings require a context to save. In most cases `kernel.root`, would serve as a reasonable context for saving settings that do not need to specifically subclassed.

# Modules
Modules allow many copies of the same class. These are opened at the context and stored in the `.opened` dictionary at a context. These are given a name which can be dynamically assigned. They are not expected to change the context at which they are opened. 

Modules are opened classes. They should be registered in the `module/<module-name>` path in the kernel. These are opened and attached to contexts. These are opened using the `open()` function on contexts and kernels. If the module, with the same namespace, is already opened, the opened module is returned and any initialization parameters are called on the `restore()` function on the given module (if it exists).

# Channels
Channels are dataflows within the kernel. For example, if a plugin is communicating over usb, it can provide a log of this communication by opening a channel. Channels are `.watch()` and `.unwatch()`.

The channels are an aspect of the Kernel. These allow channels to be opened and watched. These will convey every message sent to any watchers observing that channel. There does not need to be an open channel for that channel to be watched, or a watcher for that channel to be opened. Channels provide streams of information while being agnostic as to where the information will end up.


# Signals
Signals are a lossy update-type dataflow within the kernel. Unlike Channels, if a signal is called many times very rapidly it will result in a single trigger of the signal for the `signal_listeners`. You are not guaranteed to see every signal call, you are guaranteed to see at least one signal with the latest update. The signals will always be called in the kernels' main thread. In GUI applications this would typically be the GUI thread, thereby allowing threadsafe graphics updating.

The signaler schedules itself within the Scheduler, and provides functionality for `listen()`, `unlisten()` and `signal()`. A `@signal_listener()` attached to a life-cycle object is life-cycle aware and will `listen()` when `service_attach` or `module_open` and will `unlisten()` when `service_detach` or `module_close`. So that a Service which is not currently active will, if flagged with a `@signal_listener` only receive signals while active. This allows non-duplicating signals to send, so other instances within the kernel ecosystem know they should update, if they listened for a specific signal. The signaler does not force every message to be delivered, only the last message. 

When a listener is attached, it will get the last message for that signal if it exists. Regardless when that last signal was issued. The reason for this is that if they are used for GUI fields, they will always be given the last signal to allow fields that might not have been created when the signal was originally issued to have the most recent data.
