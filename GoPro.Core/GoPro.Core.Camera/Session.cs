using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using camera;
using common;
using common.http;
using GoPro.Core.Http;
using std;
using std.filesystem;

namespace GoPro.Core.Camera
{
	public class Session : IDisposable
	{
		protected unsafe camera.Session* mSession;

		public unsafe virtual string Server
		{
			get
			{
				camera.Session* ptr = mSession;
				if (ptr != null)
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
					basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.camera_002ESession_002Eserver(ptr, &obj);
					string result;
					try
					{
						result = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E(from_obj);
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
			set
			{
				uint num = 0u;
				camera.Session* ptr = mSession;
				if (ptr != null)
				{
					camera.Session* ptr2 = ptr;
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
					basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr3 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &value);
					try
					{
						_003CModule_003E.camera_002ESession_002Eserver(ptr2, ptr3);
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
		}

		public Session(Error err)
			: this()
		{
		}

		public unsafe Session()
		{
			mSession = (camera.Session*)CreateSession().ToPointer();
			GC.KeepAlive(this);
		}

		private unsafe void _007ESession()
		{
			//IL_0016: Expected I, but got I8
			camera.Session* ptr = mSession;
			if (ptr != null)
			{
				long num = *(long*)(*(ulong*)ptr);
				((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num)((IntPtr)ptr, 1u);
			}
			GC.KeepAlive(this);
		}

		public unsafe virtual GoPro.Core.Http.Request Handle(GoPro.Core.Http.Request request)
		{
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Request result;
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request2);
				_003CModule_003E.common_002Eclr_002EConvertRequestToCpp(&request2, request);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out optional_003Ccommon_003A_003Ahttp_003A_003AResponse_003E optional_003Ccommon_003A_003Ahttp_003A_003AResponse_003E);
					_003CModule_003E.common_002Ehttp_002ESession_002Ehandle((common.http.Session*)mSession, &optional_003Ccommon_003A_003Ahttp_003A_003AResponse_003E, &error, &request2);
					if (System.Runtime.CompilerServices.Unsafe.As<optional_003Ccommon_003A_003Ahttp_003A_003AResponse_003E, bool>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref optional_003Ccommon_003A_003Ahttp_003A_003AResponse_003E, 40)))
					{
						_003CModule_003E.common_002Ehttp_002EResponse_002E_007Bdtor_007D((common.http.Response*)(&optional_003Ccommon_003A_003Ahttp_003A_003AResponse_003E));
					}
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					result = _003CModule_003E.common_002Eclr_002EConvertRequestToClr(&request2);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request2);
					throw;
				}
				_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D(&request2);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			return result;
		}

		public unsafe virtual GoPro.Core.Http.Response Perform(basic_string_view_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_0020_003E apiToken)
		{
			//IL_0048: Expected I, but got I8
			//IL_0049: Expected I8, but got I
			//IL_004f: Expected I, but got I8
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Response result;
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request);
				_003CModule_003E.camera_002ESession_002EcreateRequest(mSession, &request, &error, apiToken);
				try
				{
					camera.Session* ptr = mSession;
					camera.Session* ptr2 = ptr;
					long num = *(long*)(*(long*)ptr + 32);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request2);
					common.http.Request* ptr3 = &request2;
					common.http.Request* ptr4 = _003CModule_003E.common_002Ehttp_002ERequest_002E_007Bctor_007D(&request2, &request);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Response response);
					long num2 = (long)(IntPtr)((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.http.Response*, common.Error*, common.http.Request*, common.http.Response*>*/)(void*)num)((IntPtr)ptr2, &response, &error, ptr4);
					try
					{
						result = _003CModule_003E.common_002Eclr_002EConvertResponseToClr((common.http.Response*)num2);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Response*, void>*/)(&_003CModule_003E.common_002Ehttp_002EResponse_002E_007Bdtor_007D), &response);
						throw;
					}
					_003CModule_003E.common_002Ehttp_002EResponse_002E_007Bdtor_007D(&response);
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					GC.KeepAlive(this);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
					throw;
				}
				_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D(&request);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}

		public unsafe virtual GoPro.Core.Http.Response Perform(GoPro.Core.Http.Request request)
		{
			//IL_0036: Expected I, but got I8
			//IL_0037: Expected I8, but got I
			//IL_003d: Expected I, but got I8
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Response result;
			try
			{
				camera.Session* ptr = mSession;
				camera.Session* ptr2 = ptr;
				long num = *(long*)(*(long*)ptr + 32);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request2);
				common.http.Request* ptr3 = &request2;
				common.http.Request* ptr4 = _003CModule_003E.common_002Eclr_002EConvertRequestToCpp(&request2, request);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Response response);
				long num2 = (long)(IntPtr)((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.http.Response*, common.Error*, common.http.Request*, common.http.Response*>*/)(void*)num)((IntPtr)ptr2, &response, &error, ptr4);
				try
				{
					result = _003CModule_003E.common_002Eclr_002EConvertResponseToClr((common.http.Response*)num2);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Response*, void>*/)(&_003CModule_003E.common_002Ehttp_002EResponse_002E_007Bdtor_007D), &response);
					throw;
				}
				_003CModule_003E.common_002Ehttp_002EResponse_002E_007Bdtor_007D(&response);
				_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
				GC.KeepAlive(this);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}

		public virtual GoPro.Core.Http.Response PerformMediaList()
		{
			return Perform(_003CModule_003E.camera_002Eapi_002E_003FA0x34d9833f_002EmediaList);
		}

		public unsafe virtual GoPro.Core.Http.Request CreateRequest(string apiToken)
		{
			//IL_0031: Expected I8, but got I
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Request result;
			try
			{
				camera.Session* ptr = mSession;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr2 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &apiToken);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request);
				try
				{
					sbyte* ptr3 = _003CModule_003E.std_002E_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002E_Myptr((_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E*)ptr2);
					ulong num2 = *(ulong*)((long)(IntPtr)ptr2 + 16);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_view_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_0020_003E obj2);
					*(long*)(&obj2) = (long)(IntPtr)ptr3;
					System.Runtime.CompilerServices.Unsafe.As<basic_string_view_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_0020_003E, ulong>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref obj2, 8)) = num2;
					_003CModule_003E.camera_002ESession_002EcreateRequest(ptr, &request, &error, obj2);
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
					result = _003CModule_003E.common_002Eclr_002EConvertRequestToClr(&request);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
					throw;
				}
				_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D(&request);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			return result;
		}

		public unsafe virtual GoPro.Core.Http.Request CreateSourceRequest(string folderFilePath)
		{
			//IL_0026: Expected I4, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Request result;
			try
			{
				camera.Session* ptr = mSession;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* source = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &folderFilePath);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out _Normal_conversion tag);
					// IL initblk instruction
					System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref tag, 0, 1);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out path path);
					_003CModule_003E.std_002Efilesystem_002E_Convert_Source_to_wide_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstruct_0020std_003A_003Afilesystem_003A_003A_Normal_conversion_003E((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path), source, tag);
					try
					{
						_003CModule_003E.camera_002ESession_002EcreateSourceRequest(ptr, &request, &error, &path, false);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<path*, void>*/)(&_003CModule_003E.std_002Efilesystem_002Epath_002E_007Bdtor_007D), &path);
						throw;
					}
					try
					{
						try
						{
							_003CModule_003E.std_002Ebasic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path));
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<wchar_t>,std::_String_val<std::_Simple_types<wchar_t> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cwchar_t_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cwchar_t_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &path);
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
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
					result = _003CModule_003E.common_002Eclr_002EConvertRequestToClr(&request);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
					throw;
				}
				_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D(&request);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			return result;
		}

		public unsafe virtual GoPro.Core.Http.Request CreateThumbnailRequest(string folderFilePath)
		{
			//IL_0026: Expected I4, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Request result;
			try
			{
				camera.Session* ptr = mSession;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* source = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &folderFilePath);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out _Normal_conversion tag);
					// IL initblk instruction
					System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref tag, 0, 1);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out path path);
					_003CModule_003E.std_002Efilesystem_002E_Convert_Source_to_wide_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstruct_0020std_003A_003Afilesystem_003A_003A_Normal_conversion_003E((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path), source, tag);
					try
					{
						_003CModule_003E.camera_002ESession_002EcreateThumbnailRequest(ptr, &request, &error, &path, false, (camera.Session.ThumbnailType)0);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<path*, void>*/)(&_003CModule_003E.std_002Efilesystem_002Epath_002E_007Bdtor_007D), &path);
						throw;
					}
					try
					{
						try
						{
							_003CModule_003E.std_002Ebasic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path));
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<wchar_t>,std::_String_val<std::_Simple_types<wchar_t> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cwchar_t_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cwchar_t_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &path);
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
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
					result = _003CModule_003E.common_002Eclr_002EConvertRequestToClr(&request);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
					throw;
				}
				_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D(&request);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			return result;
		}

		public unsafe virtual GoPro.Core.Http.Request CreateScreennailRequest(string folderFilePath)
		{
			//IL_0026: Expected I4, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Request result;
			try
			{
				camera.Session* ptr = mSession;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* source = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &folderFilePath);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out _Normal_conversion tag);
					// IL initblk instruction
					System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref tag, 0, 1);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out path path);
					_003CModule_003E.std_002Efilesystem_002E_Convert_Source_to_wide_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstruct_0020std_003A_003Afilesystem_003A_003A_Normal_conversion_003E((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path), source, tag);
					try
					{
						_003CModule_003E.camera_002ESession_002EcreateThumbnailRequest(ptr, &request, &error, &path, false, (camera.Session.ThumbnailType)1);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<path*, void>*/)(&_003CModule_003E.std_002Efilesystem_002Epath_002E_007Bdtor_007D), &path);
						throw;
					}
					try
					{
						try
						{
							_003CModule_003E.std_002Ebasic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path));
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<wchar_t>,std::_String_val<std::_Simple_types<wchar_t> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cwchar_t_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cwchar_t_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &path);
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
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
					result = _003CModule_003E.common_002Eclr_002EConvertRequestToClr(&request);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.http.Request*, void>*/)(&_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D), &request);
					throw;
				}
				_003CModule_003E.common_002Ehttp_002ERequest_002E_007Bdtor_007D(&request);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			return result;
		}

		public unsafe virtual GoPro.Core.Http.Request[] CreateLegacySphericalSourceRequest(string folderFilePath)
		{
			//Discarded unreachable code: IL_0040, IL_0052, IL_0062, IL_0072, IL_0082
			System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
			_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CD_0040EAOEJDJI_0040CreateLegacySphericalSourceRequ_0040));
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
				_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj2, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IE_0040DIGEIECN_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
					SourceLocation* ptr = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj2, &obj, 172u);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
						basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.common_002ESourceLocation_002Estring(ptr, &obj3);
						try
						{
							throw new NotImplementedException(_003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E(from_obj));
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
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<SourceLocation*, void>*/)(&_003CModule_003E.common_002ESourceLocation_002E_007Bdtor_007D), &sourceLocation);
						throw;
					}
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj2);
					throw;
				}
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
		}

		public unsafe virtual GoPro.Core.Http.Request[] CreateLegacySphericalThumbnailRequest(string folderFilePath)
		{
			//Discarded unreachable code: IL_0040, IL_0052, IL_0062, IL_0072, IL_0082
			System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
			_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CG_0040CLHOIBBE_0040CreateLegacySphericalThumbnailR_0040));
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
				_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj2, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IE_0040DIGEIECN_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
					SourceLocation* ptr = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj2, &obj, 177u);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
						basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.common_002ESourceLocation_002Estring(ptr, &obj3);
						try
						{
							throw new NotImplementedException(_003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E(from_obj));
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
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<SourceLocation*, void>*/)(&_003CModule_003E.common_002ESourceLocation_002E_007Bdtor_007D), &sourceLocation);
						throw;
					}
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj2);
					throw;
				}
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
		}

		public unsafe virtual GoPro.Core.Http.Request[] CreateLegacySphericalScreennailRequest(string folderFilePath)
		{
			//Discarded unreachable code: IL_0040, IL_0052, IL_0062, IL_0072, IL_0082
			System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
			_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CH_0040NODBBJJ_0040CreateLegacySphericalScreennail_0040));
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
				_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj2, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IE_0040DIGEIECN_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
					SourceLocation* ptr = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj2, &obj, 182u);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
						basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.common_002ESourceLocation_002Estring(ptr, &obj3);
						try
						{
							throw new NotImplementedException(_003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E(from_obj));
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
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<SourceLocation*, void>*/)(&_003CModule_003E.common_002ESourceLocation_002E_007Bdtor_007D), &sourceLocation);
						throw;
					}
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj2);
					throw;
				}
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
		}

		public unsafe virtual IntPtr ToPointer()
		{
			IntPtr result = (IntPtr)mSession;
			GC.KeepAlive(this);
			return result;
		}

		protected unsafe virtual IntPtr CreateSession()
		{
			//IL_0115: Expected I, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			IntPtr result;
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccamera_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccamera_003A_003ASession_003E_0020_003E obj);
				_003CModule_003E.std_002Emake_unique_003Cclass_0020camera_003A_003ASession_002Cstruct_0020common_003A_003AError_0020_0026_002C0_003E(&obj, &error);
				try
				{
					if (*(long*)(&obj) == 0)
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
						SourceLocation* pThis = &sourceLocation;
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
						_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj2, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0O_0040MOPBCOJO_0040CreateSession_0040));
						try
						{
							System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
							_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj3, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IE_0040DIGEIECN_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
							try
							{
								SourceLocation* location = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj3, &obj2, 95u);
								System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj4);
								common.ErrorCode errorCode;
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj4, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CD_0040IJOJOKDG_0040failed_003F5to_003F5allocate_003F5camera_003F3_003F3Sess_0040));
									try
									{
										errorCode = (common.ErrorCode)16u;
									}
									catch
									{
										//try-fault
										_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj4);
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
									_003CModule_003E.common_002EError_002Eset_003Cenum_0020common_003A_003AErrorCode_003E(&error, &errorCode, &obj4, location);
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj4);
									throw;
								}
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj4);
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj4);
									throw;
								}
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
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					long num2 = *(long*)(&obj);
					*(long*)(&obj) = 0L;
					result = (IntPtr)(void*)num2;
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<camera::Session,std::default_delete<camera::Session> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccamera_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccamera_003A_003ASession_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				_003CModule_003E.std_002Eunique_ptr_003Ccamera_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccamera_003A_003ASession_003E_0020_003E_002E_007Bdtor_007D(&obj);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			return result;
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007ESession();
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
