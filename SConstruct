# SConstruct

import os
import fnmatch
import re


env = Environment()


###############################################################################
# Globs

# See http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/BuildDirGlob

def Glob(includes = Split('*'), excludes = None, dir = '.'):
   """Similar to glob.glob, except globs SCons nodes, and thus sees
   generated files and files from build directories.  Basically, it sees
   anything SCons knows about.  A key subtlety is that since this function
   operates on generated nodes as well as source nodes on the filesystem,
   it needs to be called after builders that generate files you want to
   include.

   It will return both Dir entries and File entries
   """
   def fn_filter(node):
      fn = os.path.basename(str(node))
      match = 0
      for include in includes:
         if fnmatch.fnmatchcase( fn, include ):
            match = 1
            break

      if match == 1 and not excludes is None:
         for exclude in excludes:
            if fnmatch.fnmatchcase( fn, exclude ):
               match = 0
               break

      return match

   def filter_nodes(where):
       children = filter(fn_filter, where.all_children(scan=0))
       nodes = []
       for f in children:
           nodes.append(gen_node(f))
       return nodes

   def gen_node(n):
       """Checks first to see if the node is a file or a dir, then
       creates the appropriate node. [code seems redundant, if the node
       is a node, then shouldn't it just be left as is?
       """
       if type(n) in (type(''), type(u'')):
           path = n
       else:
           path = n.abspath
       if os.path.isdir(path):
           return Dir(n)
       else:
           return File(n)

   here = Dir(dir)
   nodes = filter_nodes(here)

   node_srcs = [n.srcnode() for n in nodes]

   src = here.srcnode()
   if src is not here:
       for s in filter_nodes(src):
           if s not in node_srcs:
               # Probably need to check if this node is a directory
               nodes.append(gen_node(os.path.join(dir,os.path.basename(str(s)))))

   return nodes

def Glob(match):
    """Similar to glob.glob, except globs SCons nodes, and thus sees
    generated files and files from build directories.  Basically, it sees
    anything SCons knows about.  A key subtlety is that since this function
    operates on generated nodes as well as source nodes on the filesystem,
    it needs to be called after builders that generate files you want to
    include."""
    def fn_filter(node):
        fn = str(node)
        return fnmatch.fnmatch(os.path.basename(fn), match)

    here = Dir('.')

    children = here.all_children()
    nodes = map(File, filter(fn_filter, children))
    node_srcs = [n.srcnode() for n in nodes]

    src = here.srcnode()
    if src is not here:
        src_children = map(File, filter(fn_filter, src.all_children()))
        for s in src_children:
            if s not in node_srcs:
                nodes.append(File(os.path.basename(str(s))))

    return nodes

###############################################################################
# ANTLR grammars

# See http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/AntlrBuilder

antlr_cmd = "java -cp /usr/share/java/antlr.jar antlr.Tool -o ${SOURCE.dir} $SOURCE"
antlr_cmd = "bin/antlr.`uname -m` -o ${SOURCE.dir} $SOURCE"

antlr_re = re.compile(r'^class\s+(\S+)\s+extends\s+(\S+)', re.MULTILINE)

def antlr_emitter(target, source, env):
        target = []
        for src in source:
                contents = src.get_contents();
		for classname, classtype in antlr_re.findall(contents):
			target.append(os.path.join(str(src.dir), classname + '.py'))
			#target.append(os.path.join(str(src.dir), classname + 'TokenTypes' + '.txt'))
        return target, source

antlr_bld = Builder(
	action = antlr_cmd, 
	src_suffix = '.g',
	emitter = antlr_emitter,
	suffix = '.notused',
)

env['BUILDERS']['Antlr'] = antlr_bld
#env.Append(ENV={'CLASSPATH':os.environ['CLASSPATH']});

aterm_sources = Flatten([
	'aterm.py', 
	env.Antlr(source = 'aterm.g')
])


###############################################################################
# Walker compilation

# See http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/UsingCodeGenerators

wc_sources = Flatten([
	'wc.py', 
	env.Antlr(source = 'wc.g'), 
	#aterm_sources,
])

wc_cmd = 'python wc.py -o $TARGET $SOURCE'

def wc_emitter(target, source, env):
    env.Depends(target, wc_sources)
    return target, source

wc_bld = Builder(
	action = wc_cmd,
	src_suffix = '.w',
	emitter = wc_emitter,
	suffix = '.py', 
)

env['BUILDERS']['WC'] = wc_bld


#env.WC(source = 'asm.w')
#env.WC(source = 'box.w')
#env.WC(source = 'ir.w')
for source in Glob('*.w'):
	env.WC(source = source)



###############################################################################
# SSL compilation

sslc_sources = Flatten([
	env.Antlr(source = 'ssl.g'),
	env.Antlr(source = 'sslc.g'),
	#aterm_sources,
])

sslc_cmd = 'python sslc.py -o $TARGET $SOURCE'

def sslc_emitter(target, source, env):
    env.Depends(target, sslc_sources)
    return target, source

sslc_bld = Builder(
	action = sslc_cmd,
	src_suffix = '.ssl',
	emitter = sslc_emitter,
	suffix = '.py', 
)

env['BUILDERS']['SSL'] = sslc_bld

env.SSL('ssl/pentium.ssl')


###############################################################################
# Unit tests

# See:
#   http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/UnitTests
#   http://spacepants.org/blog/scons-unit-test

test = env.Alias('test', env.Command('test_aterm', ['test_wc.py', aterm_sources], 'python test_aterm.py'))
test = env.Alias('test', env.Command('test_wc', ['test_wc.py', wc_sources], 'python test_wc.py'))
test = env.Alias('test', env.Command('test_ir', ['test_ir.py'], 'python test_ir.py'))
test = env.Alias('test', env.Command('test_box', ['test_box.py'], 'python test_box.py'))

# vim: set syntax=python:
