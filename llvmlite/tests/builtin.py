from llvmlite import ir
from llvmlite import binding as llvm
M = ir.Module()
i128 = ir.IntType(128)
FTy = ir.FunctionType(ir.VoidType(), [ir.PointerType(i128), ir.PointerType(i128), ir.PointerType(i128)])
F = ir.Function(M, FTy, "foo")
BB = F.append_basic_block()
IRB = ir.IRBuilder(BB)
v0 = IRB.load(F.args[1])
v1 = IRB.load(F.args[2])
res = IRB.add(v0, v1)
IRB.store(res, F.args[0])
IRB.ret_void()

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

M = llvm.parse_assembly(str(M))
M.verify()

tm = llvm.Target.from_default_triple().create_target_machine()
ee = llvm.create_mcjit_compiler(M, tm)
func = M.get_function("foo")
print(func, ee.get_function_address("foo"))
llvm.shutdown()
