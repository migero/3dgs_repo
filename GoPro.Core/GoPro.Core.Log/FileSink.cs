using System;
using System.Runtime.CompilerServices;
using System.Runtime.ExceptionServices;
using System.Runtime.InteropServices;
using System.Threading;
using common.log;
using std;

namespace GoPro.Core.Log
{
	public class FileSink : Sink, IDisposable
	{
		private unsafe shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E* mSink;

		public unsafe FileSink(string id, string path)
		{
			//Discarded unreachable code: IL_004f, IL_0069, IL_00a2, IL_00bc
			//IL_0087: Expected I, but got I8
			//IL_00d9: Expected I, but got I8
			uint num = 0u;
			((object)this)._002Ector();
			shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E* ptr = (shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E*)_003CModule_003E.@new(16uL);
			System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
			System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
			shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E* ptr5;
			try
			{
				if (ptr != null)
				{
					common.log.FileSink* ptr2 = (common.log.FileSink*)_003CModule_003E.@new(632uL);
					common.log.FileSink* px;
					try
					{
						if (ptr2 != null)
						{
							basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr3 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &path);
							try
							{
								num = 1u;
								basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr4 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj2, &id);
								try
								{
									num = 3u;
									px = _003CModule_003E.common_002Elog_002EFileSink_002E_007Bctor_007D(ptr2, ptr4, ptr3, false);
								}
								catch
								{
									//try-fault
									if ((num & 2u) != 0)
									{
										num &= 0xFFFFFFFDu;
										_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj2);
									}
									throw;
								}
							}
							catch
							{
								//try-fault
								if ((num & (true ? 1u : 0u)) != 0)
								{
									num &= 0xFFFFFFFEu;
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
								}
								throw;
							}
						}
						else
						{
							px = null;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.delete(ptr2, 632uL);
						throw;
					}
					try
					{
						try
						{
							ptr5 = _003CModule_003E.std_002Eshared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E_002E_007Bctor_007D_003Cclass_0020common_003A_003Alog_003A_003AFileSink_002C0_003E(ptr, px);
						}
						catch
						{
							//try-fault
							if ((num & 2u) != 0)
							{
								num &= 0xFFFFFFFDu;
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj2);
							}
							throw;
						}
					}
					catch
					{
						//try-fault
						if ((num & (true ? 1u : 0u)) != 0)
						{
							num &= 0xFFFFFFFEu;
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
						}
						throw;
					}
				}
				else
				{
					ptr5 = null;
				}
			}
			catch
			{
				//try-fault
				_003CModule_003E.delete(ptr, 16uL);
				throw;
			}
			try
			{
				try
				{
					mSink = ptr5;
				}
				catch
				{
					//try-fault
					if ((num & 2u) != 0)
					{
						num &= 0xFFFFFFFDu;
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj2);
					}
					throw;
				}
				if ((num & 2u) != 0)
				{
					num &= 0xFFFFFFFDu;
					try
					{
						_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj2);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj2);
						throw;
					}
				}
			}
			catch
			{
				//try-fault
				if ((num & (true ? 1u : 0u)) != 0)
				{
					num &= 0xFFFFFFFEu;
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
				}
				throw;
			}
			if ((num & (true ? 1u : 0u)) != 0)
			{
				num &= 0xFFFFFFFEu;
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
			GC.KeepAlive(this);
		}

		private unsafe void _0021FileSink()
		{
			//IL_001b: Expected I, but got I8
			//IL_002c: Expected I, but got I8
			shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E* ptr = mSink;
			if (ptr != null)
			{
				shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E* ptr2 = ptr;
				ulong num = *(ulong*)((long)(IntPtr)ptr2 + 8);
				if (num != 0L)
				{
					_003CModule_003E.std_002E_Ref_count_base_002E_Decref((_Ref_count_base*)num);
				}
				_003CModule_003E.delete(ptr2, 16uL);
				mSink = null;
			}
		}

		private void _007EFileSink()
		{
			_0021FileSink();
		}

		public unsafe override IntPtr GetNativeHandle()
		{
			IntPtr result = new IntPtr(mSink);
			GC.KeepAlive(this);
			return result;
		}

		public unsafe override shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* GetCppSinkPointer(shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* P_0)
		{
			//IL_0012: Expected I, but got I8
			uint num = 0u;
			shared_ptr_003Ccommon_003A_003Alog_003A_003AFileSink_003E* ptr = mSink;
			*(long*)P_0 = 0L;
			shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E* ptr2 = (shared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E*)((long)(IntPtr)P_0 + 8);
			*(long*)ptr2 = 0L;
			ulong num2 = *(ulong*)((long)(IntPtr)ptr + 8);
			if (num2 != 0L)
			{
				Interlocked.Increment(ref *(int*)(num2 + 8));
			}
			*(long*)P_0 = *(long*)ptr;
			*(long*)ptr2 = *(long*)((long)(IntPtr)ptr + 8);
			try
			{
				num = 1u;
				return P_0;
			}
			catch
			{
				//try-fault
				if ((num & (true ? 1u : 0u)) != 0)
				{
					num &= 0xFFFFFFFEu;
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<shared_ptr<common::log::Sink>*, void>*/)(&_003CModule_003E.std_002Eshared_ptr_003Ccommon_003A_003Alog_003A_003ASink_003E_002E_007Bdtor_007D), P_0);
				}
				throw;
			}
		}

		public unsafe void Flush()
		{
			//IL_0013: Expected I, but got I8
			//IL_0013: Expected I, but got I8
			long num = *(long*)mSink;
			((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, void>*/)(void*)(*(ulong*)(*(long*)num + 16)))((IntPtr)(void*)num);
			GC.KeepAlive(this);
		}

		public unsafe void AutoFlush([MarshalAs(UnmanagedType.U1)] bool policy)
		{
			//IL_0018: Expected I, but got I8
			//IL_0018: Expected I, but got I8
			long num = *(long*)mSink;
			long num2 = *(long*)(*(long*)num + 24);
			((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, byte, void>*/)(void*)num2)((IntPtr)(void*)num, policy ? ((byte)1) : ((byte)0));
			GC.KeepAlive(this);
		}

		[HandleProcessCorruptedStateExceptions]
		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_0021FileSink();
				return;
			}
			try
			{
				_0021FileSink();
			}
			finally
			{
				base.Finalize();
			}
		}

		public sealed override void Dispose()
		{
			Dispose(A_0: true);
			GC.SuppressFinalize(this);
			GC.KeepAlive(this);
		}

		~FileSink()
		{
			Dispose(A_0: false);
		}
	}
}
