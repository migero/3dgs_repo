using System;
using System.Runtime.CompilerServices;
using common.log;
using std;

namespace GoPro.Core.Log
{
	public abstract class Sink
	{
		public unsafe void DefaultLevel(Level level)
		{
			//IL_0053: Expected I, but got I8
			common.log.Level level2 = level switch
			{
				Level.Error => (common.log.Level)3u, 
				Level.Warn => (common.log.Level)2u, 
				Level.Info => (common.log.Level)1u, 
				Level.Debug => (common.log.Level)0u, 
				_ => (common.log.Level)4u, 
			};
			System.Runtime.CompilerServices.Unsafe.SkipInit(out shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E);
			shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* cppSinkPointer = GetCppSinkPointer(&shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E);
			try
			{
				*(common.log.Level*)(*(long*)cppSinkPointer + 64) = level2;
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<shared_ptr<common::log::Sink>*, void>*/)(&_003CModule_003E.std_002Eshared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E_002E_007Bdtor_007D), &shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E);
				throw;
			}
			if (System.Runtime.CompilerServices.Unsafe.As<shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, long>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, 8)) != 0L)
			{
				_003CModule_003E.std_002E_Ref_count_base_002E_Decref((_Ref_count_base*)System.Runtime.CompilerServices.Unsafe.As<shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, ulong>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, 8)));
			}
		}

		public unsafe void Format(string format)
		{
			//IL_0020: Expected I, but got I8
			//IL_0069: Expected I, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E);
			shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* cppSinkPointer = GetCppSinkPointer(&shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E);
			try
			{
				long num2 = *(long*)cppSinkPointer;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &format);
				try
				{
					_003CModule_003E.common_002Elog_002ESink_002Eformat((common.log.Sink*)num2, ptr);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				try
				{
					_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<shared_ptr<common::log::Sink>*, void>*/)(&_003CModule_003E.std_002Eshared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E_002E_007Bdtor_007D), &shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E);
				throw;
			}
			if (System.Runtime.CompilerServices.Unsafe.As<shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, long>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, 8)) != 0L)
			{
				_003CModule_003E.std_002E_Ref_count_base_002E_Decref((_Ref_count_base*)System.Runtime.CompilerServices.Unsafe.As<shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, ulong>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E, 8)));
			}
		}

		public abstract IntPtr GetNativeHandle();

		public unsafe abstract shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* GetCppSinkPointer(shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* P_0);

		public Sink()
		{
		}
	}
}
