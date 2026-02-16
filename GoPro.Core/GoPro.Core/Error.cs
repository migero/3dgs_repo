using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using common;
using std;

namespace GoPro.Core
{
	public class Error : IDisposable
	{
		protected unsafe common.Error* mError = null;

		public unsafe virtual IntPtr Inner
		{
			get
			{
				IntPtr result = new IntPtr(mError);
				GC.KeepAlive(this);
				return result;
			}
			set
			{
				mError = (common.Error*)value.ToPointer();
				GC.KeepAlive(this);
			}
		}

		public unsafe virtual string Description
		{
			get
			{
				common.Error* ptr = mError;
				if (ptr != null)
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
					basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr2 = _003CModule_003E.common_002EError_002Edescription(ptr, &obj);
					string result;
					try
					{
						result = new string(_003CModule_003E.std_002E_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002E_Myptr((_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E*)ptr2));
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
					GC.KeepAlive(this);
					return result;
				}
				GC.KeepAlive(this);
				return "";
			}
		}

		public unsafe virtual ErrorCode Code
		{
			get
			{
				common.Error* ptr = mError;
				if (ptr != null)
				{
					uint result = _003CModule_003E.common_002EError_002Ecode(ptr);
					GC.KeepAlive(this);
					return (ErrorCode)result;
				}
				GC.KeepAlive(this);
				return ErrorCode.ERR;
			}
		}

		public unsafe Error()
		{
			//IL_0008: Expected I, but got I8
			//IL_0027: Expected I4, but got I8
			//IL_0033: Expected I, but got I8
			common.Error* ptr = (common.Error*)_003CModule_003E.@new(176uL);
			common.Error* ptr2;
			if (ptr != null)
			{
				// IL initblk instruction
				System.Runtime.CompilerServices.Unsafe.InitBlock(ptr, 0, 176);
				ptr2 = _003CModule_003E.common_002EError_002E_007Bctor_007D(ptr);
			}
			else
			{
				ptr2 = null;
			}
			mError = ptr2;
			GC.KeepAlive(this);
		}

		private unsafe void _007EError()
		{
			common.Error* ptr = mError;
			if (ptr != null)
			{
				common.Error* ptr2 = ptr;
				_003CModule_003E.common_002EError_002E_007Bdtor_007D(ptr2);
				_003CModule_003E.delete(ptr2, 176uL);
			}
			GC.KeepAlive(this);
		}

		public unsafe void Set(ErrorCode errorCode, string description)
		{
			uint num = 0u;
			common.Error* ptr = mError;
			if (ptr != null && errorCode != 0)
			{
				common.Error* ptr2 = ptr;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
				SourceLocation* pThis = &sourceLocation;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_03CEMDFJG_0040Set_0040));
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
					_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj2, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IH_0040PDAEPELE_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
					try
					{
						SourceLocation* location = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj2, &obj, 32u);
						basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* description2;
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
						common.ErrorCode errorCode2;
						try
						{
							description2 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj3, &description);
							try
							{
								errorCode2 = (common.ErrorCode)errorCode;
							}
							catch
							{
								//try-fault
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj3);
								throw;
							}
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<SourceLocation*, void>*/)(&_003CModule_003E.common_002ESourceLocation_002E_007Bdtor_007D), pThis);
							throw;
						}
						try
						{
							_003CModule_003E.common_002EError_002Eset_003Cenum_0020common_003A_003AErrorCode_003E(ptr2, &errorCode2, description2, location);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj3);
							throw;
						}
						try
						{
							_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj3);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj3);
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj2);
						throw;
					}
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
			GC.KeepAlive(this);
		}

		[return: MarshalAs(UnmanagedType.U1)]
		public unsafe bool Success()
		{
			common.Error* ptr = mError;
			if (ptr != null)
			{
				bool num = *(int*)ptr == 0;
				GC.KeepAlive(this);
				return num;
			}
			GC.KeepAlive(this);
			return false;
		}

		[return: MarshalAs(UnmanagedType.U1)]
		public unsafe bool Failure()
		{
			common.Error* ptr = mError;
			if (ptr != null)
			{
				int num = ((*(int*)ptr != 0) ? 1 : 0);
				GC.KeepAlive(this);
				return (byte)num != 0;
			}
			GC.KeepAlive(this);
			return false;
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007EError();
			}
			else
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
	}
}
