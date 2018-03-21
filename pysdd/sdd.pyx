"""
sdd_c - SDD

__author__ = "Wannes Meert, Arthur Choi"
__license__ = "APL"

"""
cimport cython
cimport sddapi_c
cimport compiler_c
cimport io_c
cimport fnf_c
from cpython cimport array

import os
import tempfile
from contextlib import redirect_stdout, redirect_stderr
import io
import cython

wrapper_version = "1.0"


cdef class SddNode:
    cdef sddapi_c.SddNode* _sddnode
    cdef SddManager _manager
    cdef _name

    def __cinit__(self, manager):
        self._manager = manager
        self._name = "?"

    @staticmethod
    cdef wrap(sddapi_c.SddNode* node, SddManager manager):
        wrapper = SddNode(manager)
        wrapper._sddnode = node
        if sddapi_c.sdd_node_is_literal(node):
            wrapper._name = sddapi_c.sdd_node_literal(node)
        elif sddapi_c.sdd_node_is_true(node):
            wrapper._name = "True"
        elif sddapi_c.sdd_node_is_false(node):
            wrapper._name = "False"
        elif sddapi_c.sdd_node_is_decision(node):
            wrapper._name = "Decision"
        return wrapper

    def manager(self):
        return self._manager

    def is_literal(self):
        return sddapi_c.sdd_node_literal(self._sddnode)

    @property
    def literal(self):
        if not self.is_literal():
            return 0
        return sddapi_c.sdd_node_literal(self._sddnode)

    def is_true(self):
        return sddapi_c.sdd_node_is_true(self._sddnode)

    def is_false(self):
        return sddapi_c.sdd_node_is_false(self._sddnode)

    def is_decision(self):
        return sddapi_c.sdd_node_is_decision(self._sddnode)

    def conjoin(self, SddNode other):
        return self._manager.conjoin(self, other)

    def __mul__(SddNode left, SddNode right):
        return left._manager.conjoin(left, right)

    def __and__(SddNode left, SddNode right):
        return left._manager.conjoin(left, right)

    def disjoin(self, SddNode other):
        return self._manager.disjoin(self, other)

    def __add__(SddNode left, SddNode right):
        return left._manager.disjoin(left, right)

    def __or__(SddNode left, SddNode right):
        return left._manager.disjoin(left, right)

    def negate(self):
        return self._manager.negate(self)

    def __neg__(SddNode node):
        return node._manager.negate(node)

    def __invert__(SddNode node):
        return node._manager.negate(node)

    def model_count(self):
        return self._manager.model_count(self)

    def global_model_count(self):
        return self._manager.global_model_count(self)

    def size(self):
        return sddapi_c.sdd_size(self._sddnode)

    def count(self):
        return sddapi_c.sdd_count(self._sddnode)

    def elements(self):
        cdef sddapi_c.SddNode** nodes;
        nodes = sddapi_c.sdd_node_elements(self._sddnode)
        # do no free memory of nodes
        m = self.size()
        primes = [SddNode.wrap(nodes[i], self._manager) for i in range(0, 2 * m, 2)]
        subs = [SddNode.wrap(nodes[i], self._manager) for i in range(1, 2 * m, 2)]
        return zip(primes, subs)

    def wmc(self, log_mode=True):
        """Create a WmcManager to perform Weighted Model Counting with this node as root."""
        return WmcManager(self, log_mode)


    ## Manual Garbage Collection (Sec 5.4)

    def ref_count(self):
        """Returns the reference count of an SDD node.

        The reference count of a terminal SDD is 0 (terminal SDDs are always live).
        """
        return sddapi_c.sdd_ref_count(self._sddnode)

    def ref(self):
        """References an SDD node if it is not a terminal node.

        Returns the node.
        """
        # TODO: Should we ref every Python SDDNode object on creation and deref on Python GC?
        sddapi_c.sdd_ref(self._sddnode, self._manager._sddmanager)

    def deref(self):
        """Dereferences an SDD node if it is not a terminal node.

        Returns the node. The number of dereferences to a node cannot be larger than the number of its references
        (except for terminal SDD nodes, for which referencing and dereferencing has no effect).
        """
        # TODO: This means the c-pointer might be invalid at one point. Set __sddnode to None?
        sddapi_c.sdd_deref(self._sddnode, self._manager._sddmanager)


    ## File I/O

    def print_ptr(self):
        #cdef long t = <long>self._sddnode
        #print(t)
        print("{0:x}".format(<unsigned int>&self._sddnode))

    def save(self, char* filename):
        return self._manager.save(filename, self)

    def save_as_dot(self, char* filename):
        return self._manager.save_as_dot(filename, self)

    def dot(self):
        return self._manager.dot(self)

    def __str__(self):
        return "SddNode({})".format(self._name)


@cython.embedsignature(True)
cdef class SddManager:
    """Represention of a Sentential Decision Diagram.
    """
    cdef sddapi_c.SddManager* _sddmanager
    cdef bint _auto_gc_and_minimize  # TODO: replace by manager->auto_gc_and_search_on (should be identical)
    cdef CompilerOptions options
    cdef public object root

    ## Creating managers (Sec 5.1.1)

    def __init__(self, var_count=1, auto_gc_and_minimize=False, vtree=None):
        """
        Creates a new SDD manager, either given a vtree or using a balanced vtree over the given number of variables.

        :param var_count: Number of variables
        :param auto_gc_and_minimize: Automatic garbage collection
            Automatic garbage collection and automatic SDD minimization are activated in the created manager when
            auto gc and minimize is not 0.
        :param vtree: The manager copies the input vtree. Any manipulations performed by
            the manager are done on its own copy, and does not a?ect the input vtree.
        """

    def __cinit__(self, long var_count=1, bint auto_gc_and_minimize=False, Vtree vtree=None):
        self.options = CompilerOptions()
        self.root = None
        if vtree is not None:
            self._sddmanager = sddapi_c.sdd_manager_new(vtree._vtree)
            self._auto_gc_and_minimize = False
            if self._sddmanager is NULL:
                raise MemoryError("Could not create SddManager")
        else:
            self._sddmanager = sddapi_c.sdd_manager_create(var_count, auto_gc_and_minimize)
            self._auto_gc_and_minimize = auto_gc_and_minimize
            if self._sddmanager is NULL:
                raise MemoryError("Could not create SddManager")
        # Since 2.0 you have to set options and initialize values to avoid segfault
        self.set_options()

    def __dealloc__(self):
        if self._sddmanager is not NULL:
            sddapi_c.sdd_manager_free(self._sddmanager)

    @staticmethod
    def from_vtree(Vtree vtree):
        return SddManager(vtree=vtree)

    def set_options(self, options=None):
        if options is not None:
            self.options = options
        self.options.copy_options_to_c()
        sddapi_c.sdd_manager_set_options(&self.options._options, self._sddmanager)

    def add_var_before_first(self):
        """Let v be the leftmost leaf node in the vtree. A new leaf node labeled with variable n + 1 is created and
        made a left sibling of leaf v.
        """
        sddapi_c.sdd_manager_add_var_before_first(self._sddmanager)

    def add_var_after_last(self):
        """Let v be the rightmost leaf node in the vtree. A new leaf node labeled with variable n + 1 is created and
        made a right sibling of leaf v.
        """
        sddapi_c.sdd_manager_add_var_after_last(self._sddmanager)

    def add_var_before(self, sddapi_c.SddLiteral target_var):
        """Let v be the vtree leaf node labeled with variable target var. A new leaf node labeled with variable
        n + 1 is created and made a left sibling of leaf v.
        """
        sddapi_c.sdd_manager_add_var_before(target_var, self._sddmanager)

    def add_var_after(self, sddapi_c.SddLiteral target_var):
        """Let v be the vtree leaf node labeled with variable target var. A new leaf node labeled with variable
        n + 1 is created and made a right sibling of leaf v.
        """
        sddapi_c.sdd_manager_add_var_after(target_var, self._sddmanager)


    ## Terminal SDDs (Sec 5.1.2)

    def true(self):
        """Returns an SDD representing the function true."""
        return SddNode.wrap(sddapi_c.sdd_manager_true(self._sddmanager), self)

    def false(self):
        """Returns an SDD representing the function false."""
        return SddNode.wrap(sddapi_c.sdd_manager_false(self._sddmanager), self)

    def literal(self, lit):
        """Returns an SDD representing a literal.

        Returns an SDD representing a literal. The variable literal is of the form ±i, where i is an index of
        a variable, which ranges from 1 to the number of variables in the manager. If literal is positive, then
        the SDD representing the positive literal of the i-th variable is returned. If literal is negative, then
        the SDD representing the negative literal is returned.

        :param lit: Literal (number)
        """
        if lit == 0:
            raise ValueError("Literal 0 does not exist")
        if lit > self.var_count():
            raise ValueError("Number of available literals is {} < {}".format(self.var_count(), lit))
        cdef long literal_c = lit
        # if self.is_var_used(literal_c) == 0:
        #     return None # TODO in version 2.0 this is 0 if the variable is not yet in a formula
        return SddNode.wrap(sddapi_c.sdd_manager_literal(literal_c, self._sddmanager), self)

    def l(self, lit):
        """Short for literal(lit)"""
        return self.literal(lit)


    ## Automatic Garbage Collection and SDD Minimization (Sec 5.1.3)

    def auto_gc_and_minimize_on(self):
        sddapi_c.sdd_manager_auto_gc_and_minimize_on(self._sddmanager)

    def auto_gc_and_minimize_off(self):
        sddapi_c.sdd_manager_auto_gc_and_minimize_off(self._sddmanager)


    ## Size and Count (Sec 5.1.4)


    ## Misc Functions (Sec 5.1.5)

    def print_stdout(self):
        sddapi_c.sdd_manager_print(self._sddmanager)

    def var_count(self):
        """Returns the number of SDD variables currently associated with the manager."""
        return sddapi_c.sdd_manager_var_count(self._sddmanager)

    def vtree_copy(self):
        return Vtree.wrap(sddapi_c.sdd_manager_vtree_copy(self._sddmanager))

    def vtree(self):
        return Vtree.wrap(sddapi_c.sdd_manager_vtree(self._sddmanager), is_ref=True)

    def is_var_used(self, sddapi_c.SddLiteral var):
        """Returns 1 if var is referenced by a decision SDD node (dead or alive); returns 0 otherwise.

        :param var: Literal (number)
        """
        if var == 0:
            raise ValueError("Literal 0 does not exist")
        return sddapi_c.sdd_manager_is_var_used(var, self._sddmanager)


    ## Queries and Transformations (Sec 5.2.1)
    # To avoid invalidating a WMC manager, the user should refrain from performing the SDD operations of Section 5.2.1
    # when auto garbage collection and SDD minimization is active.

    def apply(self, SddNode node1, SddNode node2, sddapi_c.BoolOp op):
        if self._auto_gc_and_minimize:
            raise EnvironmentError("Transformation is not allowed when auto garbage collection and SDD minimization"
                                   "is active")
        return SddNode.wrap(sddapi_c.sdd_apply(node1._sddnode, node2._sddnode, op, self._sddmanager), self)

    def conjoin(self, SddNode node1, SddNode node2):
        if self._auto_gc_and_minimize:
            raise EnvironmentError("Transformation is not allowed when auto garbage collection and SDD minimization"
                                   "is active")
        return SddNode.wrap(sddapi_c.sdd_conjoin(node1._sddnode, node2._sddnode, self._sddmanager), self)

    def disjoin(self, SddNode node1, SddNode node2):
        if self._auto_gc_and_minimize:
            raise EnvironmentError("Transformation is not allowed when auto garbage collection and SDD minimization"
                                   "is active")
        return SddNode.wrap(sddapi_c.sdd_disjoin(node1._sddnode, node2._sddnode, self._sddmanager), self)

    def negate(self, SddNode node):
        if self._auto_gc_and_minimize:
            raise EnvironmentError("Transformation is not allowed when auto garbage collection and SDD minimization"
                                   "is active")
        return SddNode.wrap(sddapi_c.sdd_negate(node._sddnode, self._sddmanager), self)

    def global_minimize_cardinality(self, SddNode node):
        rnode = SddNode.wrap(sddapi_c.sdd_global_minimize_cardinality(node._sddnode, self._sddmanager), self)
        self.root = rnode
        return rnode

    def minimum_cardinality(self, SddNode node):
        return sddapi_c.sdd_minimum_cardinality(node._sddnode)

    def model_count(self, SddNode node):
        return sddapi_c.sdd_model_count(node._sddnode, self._sddmanager)

    def global_model_count(self, SddNode node):
        return sddapi_c.sdd_global_model_count(node._sddnode, self._sddmanager)

    ## Size and Count (Sec 5.2.2)

    def size(self):
        return sddapi_c.sdd_manager_size(self._sddmanager)

    def count(self):
        return sddapi_c.sdd_manager_count(self._sddmanager)

    def live_size(self):
        return sddapi_c.sdd_manager_live_size(self._sddmanager)

    def dead_size(self):
        return sddapi_c.sdd_manager_dead_size(self._sddmanager)

    def dead_count(self):
        return sddapi_c.sdd_manager_dead_count(self._sddmanager)


    ## File I/O (Sec 5.2.3)

    def save_as_dot(self, char* filename, SddNode node):
        sddapi_c.sdd_save_as_dot(filename, node._sddnode)

    def shared_save_as_dot(self, char* filename):
        sddapi_c.sdd_shared_save_as_dot(filename, self._sddmanager)

    def read_sdd_file(self, char* filename):
        return SddNode.wrap(sddapi_c.sdd_read(filename, self._sddmanager), self)

    def save(self, char* filename, SddNode node):
        sddapi_c.sdd_save(filename, node._sddnode)

    def dot(self, SddNode node=None):
        if node is None:
            if self.root is None:
                raise ValueError("No root node is known, pass the root node as argument")
            else:
                node = self.root
        fname = None
        cdef bytes fname_b
        cdef char* fname_c
        result = None
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = os.path.join(tmpdirname, "sdd.dot")
            fname_b = fname.encode()
            fname_c = fname_b
            self.save_as_dot(fname_c, node)
            with open(fname, "r") as ifile:
                result = ifile.read()
        return result

    @staticmethod
    def from_cnf_file(char* filename, char* vtree_type="balanced"):
        """Create an SDD from the given CNF file."""
        cdef Fnf cnf = Fnf.from_cnf_file(filename)
        vtree = Vtree(var_count=cnf.var_count, vtree_type=vtree_type)
        sdd = SddManager(vtree=vtree)
        sdd.auto_gc_and_minimize_off()  # Having this on while building triggers segfault
        # cli.initialize_manager_search_state(self._sddmanager)  # not required anymore in 2.0?
        # TODO: Add interruption to compilation (e.g. for timeouts)
        rnode = SddNode.wrap(compiler_c.fnf_to_sdd(cnf._fnf, sdd._sddmanager), sdd)
        sdd.root = rnode
        # sdd.auto_gc_and_minimize_off()
        return sdd, rnode

    def read_cnf_file(self, filename):
        """Replace the SDD by an SDD representing the theory in the given CNF file."""
        cdef Fnf cnf = Fnf.from_cnf_file(filename)
        rnode = SddNode.wrap(compiler_c.fnf_to_sdd(cnf._fnf, self._sddmanager), self)
        self.root = rnode
        return rnode

    @staticmethod
    def from_cnf_string(cnf, char* vtree_type="balanced"):
        """Create an SDD from the given CNF string."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = os.path.join(tmpdirname, "program.cnf")
            fname_b = fname.encode()
            fname_c = fname_b
            with open(fname, "w") as ofile:
                ofile.write(cnf)
            return SddManager.from_cnf_file(fname_c, vtree_type)
        return None, None

    def fnf_to_sdd(self, Fnf fnf):
        rnode = SddNode.wrap(compiler_c.fnf_to_sdd(fnf._fnf, self._sddmanager), self)
        return rnode


    ## Manual Garbage Collection (Sec 5.4)

    def garbage_collect(self):
        """Performs a global garbage collection: Claims all dead SDD nodes in the manager.
        """
        sddapi_c.sdd_manager_garbage_collect(self._sddmanager)


    ## Manual SDD Minimization (Sec 5.5)

    def minimize(self):
        # TODO: Add interruption to minimization (e.g. for timeouts)
        # TODO: Capture stdout
        sddapi_c.sdd_manager_minimize(self._sddmanager)

    def minimize_limited(self):
        sddapi_c.sdd_manager_minimize_limited(self._sddmanager)

    def init_vtree_size_limit(self, Vtree vtree):
        sddapi_c.sdd_manager_init_vtree_size_limit(vtree._vtree, self._sddmanager)

    def update_vtree_size_limit(self):
        sddapi_c.sdd_manager_update_vtree_size_limit(self._sddmanager)

    def set_vtree_search_convergence_threshold(self, float threshold):
        sddapi_c.sdd_manager_set_vtree_search_convergence_threshold(threshold, self._sddmanager)

    def set_vtree_search_time_limit(self, float time_limit):
        sddapi_c.sdd_manager_set_vtree_search_time_limit(time_limit, self._sddmanager)

    def set_vtree_fragment_time_limit(self, float time_limit):
        sddapi_c.sdd_manager_set_vtree_fragment_time_limit(time_limit, self._sddmanager)

    def set_vtree_operation_time_limit(self, float time_limit):
        sddapi_c.sdd_manager_set_vtree_operation_time_limit(time_limit, self._sddmanager)

    def set_vtree_apply_time_limit(self, float time_limit):
        sddapi_c.sdd_manager_set_vtree_apply_time_limit(time_limit, self._sddmanager)

    def set_vtree_operation_memory_limit(self, float memory_limit):
        sddapi_c.sdd_manager_set_vtree_operation_memory_limit(memory_limit, self._sddmanager)

    def set_vtree_operation_size_limit(self, float size_limit):
        sddapi_c.sdd_manager_set_vtree_operation_size_limit(size_limit, self._sddmanager)

    def set_vtree_cartesian_product_limit(self, sddapi_c.SddSize size_limit):
        sddapi_c.sdd_manager_set_vtree_cartesian_product_limit(size_limit, self._sddmanager)


    ## Printing

    def __str__(self):
        f = io.StringIO()
        with redirect_stderr(f):
            sddapi_c.sdd_manager_print(self._sddmanager)
        return f.getvalue()


cdef class Fnf:
    cdef compiler_c.Fnf* _fnf
    cdef public bint _type_cnf
    cdef public bint _type_dnf

    def __cinit__(self):
        self._type_cnf = False
        self._type_dnf = False

    def __dealloc__(self):
        if self._fnf is not NULL:
            fnf_c.free_fnf(self._fnf)

    @staticmethod
    cdef wrap(compiler_c.Fnf* fnf, cnf=False, dnf=False):
        rfnf = Fnf()
        rfnf._fnf = fnf
        return rfnf

    @property
    def var_count(self):
        return self._fnf.var_count

    @property
    def litset_count(self):
        return self._fnf.litset_count


    ## CNF/DNF to SDD Compiler (Sec 6)

    def read_cnf(self, char* filename):
        self._fnf =  io_c.read_cnf(filename)
        self._type_cnf = True
        print("Read CNF: vars={} clauses={}".format(self.var_count, self.litset_count))

    @staticmethod
    def from_cnf_file(char* filename):
        fnf = Fnf.wrap(io_c.read_cnf(filename))
        fnf._type_cnf = True
        print("Read CNF: vars={} clauses={}".format(fnf.var_count, fnf.litset_count))
        return fnf

    def read_dnf(self, char* filename):
        self._fnf =  io_c.read_dnf(filename)
        self._type_dnf = True
        print("Read CNF: vars={} clauses={}".format(self.var_count, self.litset_count))

    @staticmethod
    def from_dnf_file(char* filename):
        fnf = Fnf.wrap(io_c.read_dnf(filename))
        fnf._type_dnf = True
        print("Read CNF: vars={} clauses={}".format(fnf.var_count, fnf.litset_count))
        return fnf


@cython.embedsignature(True)
cdef class Vtree:
    cdef sddapi_c.Vtree* _vtree
    cdef public bint is_ref  # Ref does not manage memory

    ## Creating Vtrees (Sec 5.3.1)
    def __init__(self, var_count=None, var_order=None, vtree_type="balanced", filename=None):
        """
        Returns a vtree over a given number of variables.

        :param var_count: Number of variables
        :param vtree_type: The type of a vtree may be "right" (right linear), "left" (left linear), "vertical", or
            "balanced".
        :param var_order: The left-to-right variable ordering is given in array var_order. The contents of array
            var_order must be a permutation of the integers from 1 to var count.
        :return: None
        """
        pass

    def __cinit__(self, var_count=None, var_order=None, vtree_type="balanced", filename=None):
        cdef long[:] var_order_c
        cdef long var_count_c
        cdef char* vtree_type_c
        cdef char* filename_c
        self.is_ref = False
        if type(vtree_type) == str:
            vtree_type = vtree_type.encode()
            vtree_type_c = vtree_type
        elif type(vtree_type) == bytes:
            vtree_type_c = vtree_type
        else:
            raise ValueError("Invalid type for vtree_type")
        #cdef bytes type_b = type.encode()
        #cdef char* type_c = type_b
        if var_count is not None and filename is not None:
            raise ValueError("Error: Arguments var_count and filename cannot be given together")
        elif var_count is not None:
            var_count_c = var_count
            if var_order is None:
                self._vtree = sddapi_c.sdd_vtree_new(var_count_c, vtree_type_c)
            else:
                if isinstance(var_order, array.array):
                    var_order_c = var_order
                else:
                    var_order_c = array.array('l', var_order)
                self._vtree = sddapi_c.sdd_vtree_new_with_var_order(var_count_c, &var_order_c[0], vtree_type_c)
                if self._vtree is NULL:
                    raise MemoryError("Could not create Vtree")
        elif filename is not None:
            if type(filename) == str:
                filename = filename.encode()
                filename_c = filename
            elif type(filename) == bytes:
                filename_c = filename
            else:
                raise ValueError("Unknown type for filename: " + str(type(filename)))
            self._vtree = sddapi_c.sdd_vtree_read(filename_c)
            if self._vtree is NULL:
                raise MemoryError("Could not create Vtree")

    def __dealloc__(self):
        """Frees the memory of a vtree."""
        if not self.is_ref and self._vtree is not NULL:
            sddapi_c.sdd_vtree_free(self._vtree)

    @staticmethod
    def from_file(filename):
        """Create Vtree from file."""
        return Vtree(filename=filename)

    @staticmethod
    cdef wrap(sddapi_c.Vtree* vtree, is_ref=False):
        """Transform a C Vtree to a Python Vtree.
        
        :param vtree: C-pointer to vtree
        :param is_ref: True if memory should not be managed by this Python object
        :return: Python object for Vtree
        """
        if vtree == NULL:
            return None
        rvtree = Vtree()
        rvtree._vtree = vtree
        rvtree.is_ref = is_ref
        return rvtree


    ## Size and Count (Sec 5.3.2)

    def size(self):
        return sddapi_c.sdd_vtree_size(self._vtree)

    def live_size(self):
        return sddapi_c.sdd_vtree_live_size(self._vtree)

    def dead_size(self):
        return sddapi_c.sdd_vtree_dead_size(self._vtree)

    def count(self):
        return sddapi_c.sdd_vtree_count(self._vtree)

    def live_count(self):
        return sddapi_c.sdd_vtree_live_count(self._vtree)

    def dead_count(self):
        return sddapi_c.sdd_vtree_dead_count(self._vtree)

    def size_at(self):
        return sddapi_c.sdd_vtree_size_at(self._vtree)

    def live_size_at(self):
        return sddapi_c.sdd_vtree_live_size_at(self._vtree)

    def dead_size_at(self):
        return sddapi_c.sdd_vtree_dead_size_at(self._vtree)

    def count_at(self):
        return sddapi_c.sdd_vtree_count_at(self._vtree)

    def live_count_at(self):
        return sddapi_c.sdd_vtree_live_count_at(self._vtree)

    def dead_count_at(self):
        return sddapi_c.sdd_vtree_dead_count_at(self._vtree)


    ## File I/O (Sec 5.3.3)

    def save(self, char* filename):
        """Saves a vtree to file."""
        sddapi_c.sdd_vtree_save(filename, self._vtree)

    def read(self, char* filename):
        """Reads a vtree from file."""
        self._vtree = sddapi_c.sdd_vtree_read(filename)

    def save_as_dot(self, char* filename):
        sddapi_c.sdd_vtree_save_as_dot(filename, self._vtree)

    def dot(self):
        """Vtree to Graphiv dot string."""
        fname = None
        cdef bytes fname_b
        cdef char* fname_c
        result = None
        with tempfile.TemporaryDirectory() as tmpdirname:
            fname = os.path.join(tmpdirname, "vtree.dot")
            fname_b = fname.encode()
            fname_c = fname_b
            self.save_as_dot(fname_c)
            with open(fname, "r") as ifile:
                result = ifile.read()
        return result


    ## Navigation (Sec 5.3.4)

    def is_leaf(self):
        """Returns 1 if vtree is a leaf node, and 0 otherwise."""
        return sddapi_c.sdd_vtree_is_leaf(self._vtree)

    def left(self):
        """Returns the left child of a vtree node
        (returns NULL if the vtree is a leaf node).
        """
        return Vtree.wrap(sddapi_c.sdd_vtree_left(self._vtree), is_ref=True)

    def right(self):
        """Returns the right child of a vtree node
        (returns NULL if the vtree is a leaf node).
        """
        return Vtree.wrap(sddapi_c.sdd_vtree_right(self._vtree), is_ref=True)

    def parent(self):
        """Returns the parent of a vtree node
        (return NULL if the vtree is a root node).
        """
        return Vtree.wrap(sddapi_c.sdd_vtree_parent(self._vtree), is_ref=True)


    ## Edit Operations (Sec 5.3.5)

    def rotate_left(self, SddManager sddmanager, int limited):
        """Rotates a vtree node left, given time and size limits.

        Time and size limits, among others, are enforced when limited is set to 1; if limited is set to 0,
        limits are deactivated.
        Returns 1 if the operation succeeds and 0 otherwise (i.e., limits exceeded).
        This operation assumes no dead SDD nodes inside or above vtree and does not introduce any new dead SDD nodes.
        """
        return sddapi_c.sdd_vtree_rotate_left(self._vtree, sddmanager._sddmanager, limited)

    def rotate_right(self, SddManager sddmanager, int limited):
        """Rotates a vtree node right, given time, size and cartesian-product limits.

        Time and size limits, among others, are enforced when limited is set to 1; if limited is set to 0,
        limits are deactivated.
        Returns 1 if the operation succeeds and 0 otherwise (i.e., limits exceeded).
        This operation assumes no dead SDD nodes inside or above vtree and does not introduce any new dead SDD nodes.
        """
        return sddapi_c.sdd_vtree_rotate_right(self._vtree, sddmanager._sddmanager, limited)

    def swap(self, SddManager sddmanager, int limited):
        """Swaps the children of a vtree node, given time, size and cartesian-product limits.

        Time and size limits, among others, are enforced when limited is set to 1; if limited is set to 0,
        limits are deactivated.
        Returns 1 if the operation succeeds and 0 otherwise (i.e., limits exceeded).
        This operation assumes no dead SDD nodes inside or above vtree and does not introduce any new dead SDD nodes.

        A size limit is interpreted using a context which consists of two elements. First, a vtree v which is used to
        define the live SDD nodes whose size is to be constrained by the limit. Second, an initial size s to be used
        as a reference point when measuring the amount of size increase. That is, a limit l will constrain the size
        of live SDD nodes in vtree v to <= l * s.
        """
        return sddapi_c.sdd_vtree_swap(self._vtree, sddmanager._sddmanager, limited)


    ## Misc Functions (Sec 5.3.7)

    @staticmethod
    def is_sub(Vtree vtree1, Vtree vtree2):
        """Returns 1 if vtree1 is a sub-vtree of vtree2 and 0 otherwise."""
        cdef bint rval
        rval = sddapi_c.sdd_vtree_is_sub(vtree1._vtree, vtree2._vtree)
        return rval

    @staticmethod
    def lca(Vtree vtree1, Vtree vtree2, Vtree root):
        """Returns the lowest common ancestor (lca) of vtree nodes vtree1 and vtree2, assuming that root is a common
        ancestor of these two nodes.
        """
        return Vtree.wrap(sddapi_c.sdd_vtree_lca(vtree1._vtree, vtree2._vtree, root._vtree))

    def var_count(self):
        """Returns the number of variables contained in the vtree."""
        return sddapi_c.sdd_vtree_var_count(self._vtree)

    def var(self):
        """Returns the variable associated with a vtree node.

         If the vtree node is a leaf, and returns 0 otherwise.
         """
        return sddapi_c.sdd_vtree_var(self._vtree)

    def position(self):
        """Returns the position of a given vtree node in the vtree inorder.

        Position indices start at 0.
        """
        return sddapi_c.sdd_vtree_position(self._vtree)

    def location(self, SddManager manager):
        """Returns the location of the pointer to the vtree root.

        This location can be used to access the new root of the vtree, which may have changed due to rotating some
        of the vtree nodes.
        """
        # cdef Vtree** vtreepp;
        sddapi_c.sdd_vtree_location(self._vtree, manager._sddmanager)
        # TODO: Pointer Pointer not supported by Cython. Is this function really necessary?


@cython.embedsignature(True)
cdef class WmcManager:
    cdef sddapi_c.WmcManager* _wmcmanager

    ## Weighted Model Counting (Sec 5.6)

    def __init__(self, node, log_mode=1):
        """
        Creates a WMC manager for the SDD rooted at node and initializes literal weights. When log mode =6 0, all
        computations done by the manager will be in natural log-space. Literal weights are initialized to 0 in
        log-mode and to 1 otherwise. A number of functions are given below for passing values to, or recovering
        values from, a WMC manager. In log-mode, all these values are in natural logs. Finally, a WMC manager may
        become invalid if garbage collection or SDD minimization takes place.

        Note: To avoid invalidating a WMC manager, the user should refrain from performing the SDD operations like
        queries and transformations when auto garbage collection and SDD minimization is active.

        Background:

        Weighted model counting (WMC) is performed with respect to a given SDD and literal weights, and is based on
        the following definitions:

        * The weight of a variable instantiation is the product of weights assigned to its literals.
        * The weighted model count of the SDD is the sum of weights attained by its models. Here, a model is an
          instantiation (of all variables in the manager) that satis?es the SDD.
        * The weighted model count of a literal is the sum of weights attained by its models that are also models of
          the given SDD.
        * The probability of a literal is the ratio of its weighted model count over the one for the given SDD.

        To facilitate the computation of weighted model counts with respect to changing literal weights, a WMC manager
        is created for the given SDD. This manager stores the weights of literals, allowing one to change them, and
        to recompute the corresponding weighted model count each time the weights change.
        """
        pass

    def __cinit__(self, SddNode node, bint log_mode=1):
        self._wmcmanager = sddapi_c.wmc_manager_new(node._sddnode, log_mode, node._manager._sddmanager)
        if self._wmcmanager is NULL:
            raise MemoryError()

    def __dealloc__(self):
        if self._wmcmanager is not NULL:
            sddapi_c.wmc_manager_free(self._wmcmanager)

    @property
    def zero_weight(self):
        """Returns -inf for log-mode and 0 otherwise."""
        return sddapi_c.wmc_zero_weight(self._wmcmanager)

    @property
    def one_weight(self):
        """Returns 0 for log-mode and 1 otherwise."""
        return sddapi_c.wmc_one_weight(self._wmcmanager)

    def propagate(self):
        """Returns the weighted model count of the SDD underlying the WMC manager (using the current literal weights).

        This function should be called each time the weights of literals are changed.
        """
        return sddapi_c.wmc_propagate(self._wmcmanager)

    def set_literal_weight(self, literal, sddapi_c.SddWmc weight):
        """Set weight of literal.

        Sets the weight of a literal in the given WMC manager (should pass the natural log of the weight in log-mode).

        This is a slow function, to set one or more literal weights fast use
        set_literal_weights_from_array.
        """
        cdef sddapi_c.SddLiteral literal_c = self._extract_literal(literal)
        sddapi_c.wmc_set_literal_weight(literal_c, weight, self._wmcmanager)

    def set_literal_weights_from_array(self, double[:] weights):
        """Set all literal weights.

        Expects an array of size <nb_literals>*2 which represents literals [-3, -2, -1, 1, 2, 3]
        """
        cdef long nb_lits = len(weights) / 2
        cdef sddapi_c.SddLiteral lit
        cdef long i
        for i in range(nb_lits):
            sddapi_c.wmc_set_literal_weight(i - nb_lits, weights[i], self._wmcmanager)
        for i in range(nb_lits, 2*nb_lits):
            sddapi_c.wmc_set_literal_weight(i - nb_lits + 1, weights[i], self._wmcmanager)

    def literal_weight(self, literal):
        """Returns the weight of a literal."""
        cdef sddapi_c.SddLiteral literal_c = self._extract_literal(literal)
        return sddapi_c.wmc_literal_weight(literal_c, self._wmcmanager)

    def literal_derivative(self, literal):
        """Returns the partial derivative of the weighted model count with respect to the weight of literal.

        The result returned by this function is meaningful only after having called wmc propagate.
        """
        cdef sddapi_c.SddLiteral literal_c = self._extract_literal(literal)
        return sddapi_c.wmc_literal_derivative(literal_c, self._wmcmanager)

    def literal_pr(self, literal):
        """Returns the probability of literal.

        The result returned by this function is meaningful only after having called wmc propagate.
        """
        cdef sddapi_c.SddLiteral literal_c = self._extract_literal(literal)
        return sddapi_c.wmc_literal_pr(literal_c, self._wmcmanager)


    ## Auxiliary

    def _extract_literal(self, literal):
        cdef sddapi_c.SddLiteral literal_c
        if isinstance(literal, SddNode):
            if literal.is_literal():
                literal_c = literal.literal
            else:
                raise TypeError("Formula/node needs to be a literal")
        else:
            literal_c = literal
        return literal_c


cdef class CompilerOptions:
    cdef compiler_c.SddCompilerOptions _options
    cdef public object cnf_filename
    cdef public object dnf_filename
    cdef public object vtree_filename
    cdef public object sdd_filename
    cdef public object output_vtree_filename
    cdef public object output_vtree_dot_filename
    cdef public object output_sdd_filename
    cdef public object output_sdd_dot_filename
    cdef public int minimize_cardinality
    cdef public object initial_vtree_type
    cdef public int vtree_search_mode
    cdef public int post_search
    cdef public int verbose

    def __init__(self, cnf_filename = None, dnf_filename = None, vtree_filename = None, sdd_filename = None,
                  output_vtree_filename = None, output_vtree_dot_filename = None, output_sdd_filename = None,
                  output_sdd_dot_filename = None, initial_vtree_type = "balanced".encode(),
                  minimize_cardinality = 0, vtree_search_mode = -1, post_search = 0, verbose = 0):
        pass

    def __cinit__(self, cnf_filename = None, dnf_filename = None, vtree_filename = None, sdd_filename = None,
                  output_vtree_filename = None, output_vtree_dot_filename = None, output_sdd_filename = None,
                  output_sdd_dot_filename = None, initial_vtree_type = "balanced".encode(),
                  minimize_cardinality = 0, vtree_search_mode = -1, post_search = 0, verbose = 0):
        self.cnf_filename = cnf_filename
        self.dnf_filename = dnf_filename
        self.vtree_filename = vtree_filename
        self.sdd_filename = sdd_filename
        self.output_vtree_filename = output_vtree_filename
        self.output_vtree_dot_filename = output_vtree_dot_filename
        self.output_sdd_filename = output_sdd_filename
        self.output_sdd_dot_filename = output_sdd_dot_filename
        self.initial_vtree_type = initial_vtree_type
        self.minimize_cardinality = minimize_cardinality
        self.vtree_search_mode = vtree_search_mode
        self.post_search = post_search
        self.verbose = verbose

    def copy_options_to_c(self):
        if self.cnf_filename is None:
            self._options.cnf_filename = NULL
        else:
            self._options.cnf_filename = self.cnf_filename
        if self.dnf_filename is None:
            self._options.dnf_filename = NULL
        else:
            self._options.dnf_filename = self.dnf_filename
        if self.vtree_filename is None:
            self._options.vtree_filename = NULL
        else:
            self._options.vtree_filename = self.vtree_filename
        if self.sdd_filename is None:
            self._options.sdd_filename = NULL
        else:
            self._options.sdd_filename = self.sdd_filename
        if self.output_vtree_filename is None:
            self._options.output_vtree_filename = NULL
        else:
            self._options.output_vtree_filename = self.output_vtree_filename
        if self.output_vtree_dot_filename is None:
            self._options.output_vtree_dot_filename = NULL
        else:
            self._options.output_vtree_dot_filename = self.output_vtree_dot_filename
        if self.output_sdd_filename is None:
            self._options.output_sdd_filename = NULL
        else:
            self._options.output_sdd_filename = self.output_sdd_filename
        if self.output_sdd_dot_filename is None:
            self._options.output_sdd_dot_filename = NULL
        else:
            self._options.output_sdd_dot_filename = self.output_sdd_dot_filename
        self._options.minimize_cardinality  = self.minimize_cardinality
        self._options.vtree_search_mode  = self.vtree_search_mode
        self._options.post_search  = self.post_search
        self._options.verbose  = self.verbose

    def __str__(self):
        r = "CompilerOptions:\n"
        r += "  cnf_filename: " + str(self.cnf_filename) + "\n"
        r += "  dnf_filename: " + str(self.dnf_filename) + "\n"
        r += "  vtree_filename: " + str(self.vtree_filename) + "\n"
        r += "  sdd_filename: " + str(self.sdd_filename) + "\n"
        r += "  output_vtree_filename: " + str(self.output_vtree_filename) + "\n"
        r += "  output_vtree_dot_filename: " + str(self.output_vtree_dot_filename) + "\n"
        r += "  output_sdd_filename: " + str(self.output_sdd_filename) + "\n"
        r += "  output_sdd_dot_filename: " + str(self.output_sdd_dot_filename) + "\n"
        r += "  initial_vtree_type: " + str(self.initial_vtree_type) + "\n"
        r += "  minimize_cardinality: " + str(self.minimize_cardinality) + "\n"
        r += "  vtree_search_mode: " + str(self.vtree_search_mode) + "\n"
        r += "  post_search: " + str(self.post_search) + "\n"
        r += "  verbose: " + str(self.verbose) + "\n"
        return r
