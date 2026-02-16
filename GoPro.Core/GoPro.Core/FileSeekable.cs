using System;
using System.Runtime.CompilerServices;
using common;
using common.io;
using std;

namespace GoPro.Core
{
	public class FileSeekable : Seekable
	{
		public unsafe FileSeekable(string path, Mode mode)
		{
			//IL_007a: Expected I, but got I8
			uint num = 0u;
			((object)this)._002Ector();
			try
			{
				if (string.IsNullOrEmpty(path))
				{
					throw new ArgumentNullException("invalid url");
				}
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				try
				{
					common.io.Mode mode2 = (common.io.Mode)mode;
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
					basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* _003C_Args_1_003E = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &path);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccommon_003A_003Aio_003A_003AFile_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003AFile_003E_0020_003E obj2);
					try
					{
						_003CModule_003E.std_002Emake_unique_003Cclass_0020common_003A_003Aio_003A_003AFile_002Cstruct_0020common_003A_003AError_0020_0026_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cenum_0020common_003A_003Aio_003A_003AMode_002C0_003E(&obj2, &error, _003C_Args_1_003E, &mode2);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
						throw;
					}
					try
					{
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
						_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
						long num2 = *(long*)(&obj2);
						*(long*)(&obj2) = 0L;
						IntPtr intPtr2 = (base.Pointer = (IntPtr)(void*)num2);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<common::io::File,std::default_delete<common::io::File> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Aio_003A_003AFile_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003AFile_003E_0020_003E_002E_007Bdtor_007D), &obj2);
						throw;
					}
					_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Aio_003A_003AFile_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003AFile_003E_0020_003E_002E_007Bdtor_007D(&obj2);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
					throw;
				}
				_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
				GC.KeepAlive(this);
				return;
			}
			catch
			{
				//try-fault
				base.Dispose(A_0: true);
				throw;
			}
		}
	}
}
