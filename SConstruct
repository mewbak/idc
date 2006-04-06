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

antlr_res={}

def make_re(classtype):
        return re.compile('^class\\s+(\\S+)\\s+extends\\s+'+classtype,re.MULTILINE)

def append_re(res,classtype,fn):
        res[classtype]=[make_re(classtype),fn]

def lexer_append(target,classname):
        target_append(target, classname)
        #target.append(classname+'TokenTypes'+'.txt')

def target_append(target,classname):
        target.append(classname+'.py')

append_re(antlr_res,'Lexer',lexer_append)
append_re(antlr_res,'Parser',target_append)
append_re(antlr_res,'TreeParser',target_append)

def antlr_emitter(target,source,env):
        target = []
        for src in source:
                contents = src.get_contents();
                for type_re in antlr_res:
                        found = antlr_res[type_re][0].findall(contents)
                        for classname in found:
                                antlr_res[type_re][1](target,classname)
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

wgen_sources = Flatten([
	'wgen.py', 
	env.Antlr(source = 'wgen.g'), 
	#aterm_sources,
])

wgen_cmd = 'python wgen.py -o $TARGET $SOURCE'

def wgen_emitter(target, source, env):
    env.Depends(target, wgen_sources)
    return target, source

wgen_bld = Builder(
	action = wgen_cmd,
	src_suffix = '.w',
	emitter = wgen_emitter,
	suffix = '.py', 
)

env['BUILDERS']['WGen'] = wgen_bld


#env.WGen(source = 'asm.w')
#env.WGen(source = 'box.w')
#env.WGen(source = 'ir.w')
for source in Glob('*.w'):
	env.WGen(source = source)



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

# See http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/UnitTests
# http://spacepants.org/blog/scons-unit-test


# vim: set syntax=python:
