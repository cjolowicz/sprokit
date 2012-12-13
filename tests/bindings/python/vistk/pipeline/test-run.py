#!@PYTHON_EXECUTABLE@
#ckwg +4
# Copyright 2011-2012 by Kitware, Inc. All Rights Reserved. Please refer to
# KITWARE_LICENSE.TXT for licensing information, or contact General Counsel,
# Kitware, Inc., 28 Corporate Drive, Clifton Park, NY 12065.


def make_source(conf):
    from vistk.pipeline import process

    class Source(process.PythonProcess):
        def __init__(self, conf):
            process.PythonProcess.__init__(self, conf)

            self.conf_start = 'start'
            self.conf_end = 'end'

            self.declare_configuration_key(self.conf_start, str(0), 'Starting number')
            self.declare_configuration_key(self.conf_end, str(10), 'Ending number')

            self.port_output = 'number'

            required = process.PortFlags()
            required.add(self.flag_required)

            self.declare_output_port(self.port_output, 'integer', required, 'output port')

        def _configure(self):
            self.counter = int(self.config_value(self.conf_start))
            self.end = int(self.config_value(self.conf_end))

            self._base_configure()

        def _step(self):
            from vistk.pipeline import datum

            if self.counter >= self.end:
                self.mark_process_as_complete()
                dat = datum.complete()
            else:
                dat = datum.new(self.counter)
                self.counter += 1

            self.push_datum_to_port(self.port_output, dat)

            self._base_step()

    return Source(conf)


def make_sink(conf):
    from vistk.pipeline import process

    class Sink(process.PythonProcess):
        def __init__(self, conf):
            process.PythonProcess.__init__(self, conf)

            self.conf_output = 'output'

            self.declare_configuration_key(self.conf_output, 'output.txt', 'Output file name')

            self.port_input = 'number'

            required = process.PortFlags()
            required.add(self.flag_required)

            self.declare_input_port(self.port_input, 'integer', required, 'input port')

        def _configure(self):
            output = self.config_value(self.conf_output)

            self.fout = open(output, 'w+')

            self._base_configure()

        def _step(self):
            from vistk.pipeline import datum

            num = self.grab_value_from_port(self.port_input)

            self.fout.write('%d\n' % num)
            self.fout.flush()

            self._base_step()

    return Sink(conf)


def create_process(type, name, conf):
    from vistk.pipeline import modules
    from vistk.pipeline import process_registry

    modules.load_known_modules()

    reg = process_registry.ProcessRegistry.self()

    p = reg.create_process(type, name, conf)

    return p


def run_pipeline(sched_type, pipe, conf):
    from vistk.pipeline import config
    from vistk.pipeline import modules
    from vistk.pipeline import scheduler_registry

    modules.load_known_modules()

    reg = scheduler_registry.SchedulerRegistry.self()

    s = reg.create_scheduler(sched_type, pipe, conf)

    s.start()
    s.wait()


def check_file(fname, expect):
    with open(fname, 'r') as fin:
        ints = list([int(l.strip()) for l in list(fin)])

        num_ints = len(ints)
        num_expect = len(expect)

        if not num_ints == num_expect:
            test_error("Got %d results when %d were expected." % (num_ints, num_expect))

        res = list(zip(ints, expect))

        line = 1

        for i, e in res:
            if not i == e:
                test_error("Result %d is %d, where %d was expected" % (line, i, e))
            line += 1


def test_python_to_python(sched_type):
    from vistk.pipeline import config
    from vistk.pipeline import pipeline
    from vistk.pipeline import process

    name_source = 'source'
    name_sink = 'sink'

    port_output = 'number'
    port_input = 'number'

    min = 0
    max = 10
    output_file = 'test-python-run-python_to_python.txt'

    c = config.empty_config()

    c.set_value(process.PythonProcess.config_name, name_source)
    c.set_value('start', str(min))
    c.set_value('end', str(max))

    s = make_source(c)

    c = config.empty_config()

    c.set_value(process.PythonProcess.config_name, name_sink)
    c.set_value('output', output_file)

    t = make_sink(c)

    p = pipeline.Pipeline(c)

    p.add_process(s)
    p.add_process(t)

    p.connect(name_source, port_output,
              name_sink, port_input)

    p.setup_pipeline()

    run_pipeline(sched_type, p, c)

    check_file(output_file, list(range(min, max)))


def test_cpp_to_python(sched_type):
    from vistk.pipeline import config
    from vistk.pipeline import pipeline
    from vistk.pipeline import process

    name_source = 'source'
    name_sink = 'sink'

    port_output = 'number'
    port_input = 'number'

    min = 0
    max = 10
    output_file = 'test-python-run-cpp_to_python.txt'

    c = config.empty_config()

    c.set_value('start', str(min))
    c.set_value('end', str(max))

    s = create_process('numbers', name_source, c)

    c = config.empty_config()

    c.set_value(process.PythonProcess.config_name, name_sink)
    c.set_value('output', output_file)

    t = make_sink(c)

    p = pipeline.Pipeline()

    p.add_process(s)
    p.add_process(t)

    p.connect(name_source, port_output,
              name_sink, port_input)

    p.setup_pipeline()

    run_pipeline(sched_type, p, c)

    check_file(output_file, list(range(min, max)))


def test_python_to_cpp(sched_type):
    from vistk.pipeline import config
    from vistk.pipeline import pipeline
    from vistk.pipeline import process

    name_source = 'source'
    name_sink = 'sink'

    port_output = 'number'
    port_input = 'number'

    min = 0
    max = 10
    output_file = 'test-python-run-python_to_cpp.txt'

    c = config.empty_config()

    c.set_value(process.PythonProcess.config_name, name_source)
    c.set_value('start', str(min))
    c.set_value('end', str(max))

    s = make_source(c)

    c = config.empty_config()

    c.set_value('output', output_file)

    t = create_process('print_number', name_sink, c)

    p = pipeline.Pipeline()

    p.add_process(s)
    p.add_process(t)

    p.connect(name_source, port_output,
              name_sink, port_input)

    p.setup_pipeline()

    run_pipeline(sched_type, p, c)

    check_file(output_file, list(range(min, max)))


def test_python_via_cpp(sched_type):
    from vistk.pipeline import config
    from vistk.pipeline import pipeline
    from vistk.pipeline import process

    name_source1 = 'source1'
    name_source2 = 'source2'
    name_mult = 'mult'
    name_sink = 'sink'

    port_output = 'number'
    port_input1 = 'src/1'
    port_input2 = 'src/2'
    port_output1 = 'out/1'
    port_output2 = 'out/2'
    port_factor1 = 'factor1'
    port_factor2 = 'factor2'
    port_product = 'product'
    port_input = 'number'

    min1 = 0
    max1 = 10
    min2 = 10
    max2 = 15
    output_file = 'test-python-run-python_via_cpp.txt'

    c = config.empty_config()

    c.set_value(process.PythonProcess.config_name, name_source1)
    c.set_value('start', str(min1))
    c.set_value('end', str(max1))

    s1 = make_source(c)

    c = config.empty_config()

    c.set_value(process.PythonProcess.config_name, name_source2)
    c.set_value('start', str(min2))
    c.set_value('end', str(max2))

    s2 = make_source(c)

    c = config.empty_config()

    m = create_process('multiplication', name_mult, c)

    c = config.empty_config()

    c.set_value(process.PythonProcess.config_name, name_sink)
    c.set_value('output', output_file)

    t = make_sink(c)

    p = pipeline.Pipeline()

    p.add_process(s1)
    p.add_process(s2)
    p.add_process(m)
    p.add_process(t)

    p.connect(name_source1, port_output,
              name_mult, port_factor1)
    p.connect(name_source2, port_output,
              name_mult, port_factor2)
    p.connect(name_mult, port_product,
              name_sink, port_input)

    p.setup_pipeline()

    run_pipeline(sched_type, p, c)

    check_file(output_file, [a * b for a, b in zip(list(range(min1, max1)), list(range(min2, max2)))])


def main(testname, sched_type):
    if testname == 'python_to_python':
        test_python_to_python(sched_type)
    elif testname == 'cpp_to_python':
        test_cpp_to_python(sched_type)
    elif testname == 'python_to_cpp':
        test_python_to_cpp(sched_type)
    elif testname == 'python_via_cpp':
        test_python_via_cpp(sched_type)
    else:
        test_error("No such test '%s'" % testname)


if __name__ == '__main__':
    import os
    import sys

    if not len(sys.argv) == 4:
        test_error("Expected three arguments")
        sys.exit(1)

    (testname, sched_type) = tuple(sys.argv[1].split('-', 1))

    os.chdir(sys.argv[2])

    sys.path.append(sys.argv[3])

    from vistk.test.test import *

    try:
        main(testname, sched_type)
    except BaseException as e:
        test_error("Unexpected exception: %s" % str(e))