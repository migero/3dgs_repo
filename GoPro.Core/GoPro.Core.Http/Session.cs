using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using common;
using common.http;
using GoPro.Core.Cloud;
using std;

namespace GoPro.Core.Http
{
	public class Session : IDisposable
	{
		protected unsafe common.http.Session* mSession;

		public unsafe IntPtr Pointer
		{
			get
			{
				IntPtr result = (IntPtr)mSession;
				GC.KeepAlive(this);
				return result;
			}
			protected set
			{
				mSession = (common.http.Session*)value.ToPointer();
				GC.KeepAlive(this);
			}
		}

		public unsafe string UserAgent
		{
			get
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.common_002Ehttp_002ESession_002EuserAgent(mSession, &obj);
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
			set
			{
				uint num = 0u;
				common.http.Session* ptr = mSession;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr2 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &value);
				try
				{
					_003CModule_003E.common_002Ehttp_002ESession_002EuserAgent(ptr, ptr2);
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
			}
		}

		public unsafe Session()
		{
			//IL_0112: Expected I, but got I8
			uint num = 0u;
			base._002Ector();
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccommon_003A_003Ahttp_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Ahttp_003A_003ASession_003E_0020_003E obj);
				_003CModule_003E.std_002Emake_unique_003Cclass_0020common_003A_003Ahttp_003A_003ASession_002Cstruct_0020common_003A_003AError_0020_0026_002C0_003E(&obj, &error);
				try
				{
					if (*(long*)(&obj) == 0)
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
						SourceLocation* pThis = &sourceLocation;
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
						_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj2, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_07FFOFCADM_0040Session_0040));
						try
						{
							System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
							_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj3, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IJ_0040NJLLLBLG_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
							try
							{
								SourceLocation* location = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj3, &obj2, 22u);
								System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj4);
								common.ErrorCode errorCode;
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj4, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CB_0040OLAMBMAL_0040failed_003F5to_003F5allocate_003F5http_003F3_003F3Sessio_0040));
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
					common.http.Session* ptr = (common.http.Session*)(*(ulong*)(&obj));
					*(long*)(&obj) = 0L;
					mSession = ptr;
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<common::http::Session,std::default_delete<common::http::Session> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Ahttp_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Ahttp_003A_003ASession_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Ahttp_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Ahttp_003A_003ASession_003E_0020_003E_002E_007Bdtor_007D(&obj);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
		}

		private unsafe void _007ESession()
		{
			//IL_0016: Expected I, but got I8
			common.http.Session* ptr = mSession;
			if (ptr != null)
			{
				long num = *(long*)(*(ulong*)ptr);
				((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num)((IntPtr)ptr, 1u);
			}
			GC.KeepAlive(this);
		}

		public unsafe virtual Response Perform(Request request)
		{
			//IL_0036: Expected I, but got I8
			//IL_0037: Expected I8, but got I
			//IL_003d: Expected I, but got I8
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			Response result;
			try
			{
				common.http.Session* ptr = mSession;
				common.http.Session* ptr2 = ptr;
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

		public unsafe Task<Response> PerformAsync(Request request)
		{
			//IL_004e: Expected I, but got I8
			HttpTaskCompletion httpTaskCompletion = new HttpTaskCompletion();
			common.http.Session* ptr = mSession;
			common.http.Session* ptr2 = ptr;
			long num = *(long*)(*(long*)ptr + 24);
			System.Runtime.CompilerServices.Unsafe.SkipInit(out function_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E obj);
			function_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E* pThis = &obj;
			function_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E* ptr3 = httpTaskCompletion.get_HttpCompletion(&obj);
			common.http.Request* ptr5;
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request2);
				common.http.Request* ptr4 = &request2;
				ptr5 = _003CModule_003E.common_002Eclr_002EConvertRequestToCpp(&request2, request);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<function<void __cdecl(common::Error &,common::http::Request &,common::http::Response &)>*, void>*/)(&_003CModule_003E.std_002Efunction_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E_002E_007Bdtor_007D), pThis);
				throw;
			}
			((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.http.Request*, function<void __cdecl(common::Error &,common::http::Request &,common::http::Response &)>*, void>*/)(void*)num)((IntPtr)ptr2, ptr5, ptr3);
			Task<Response> completionTask = httpTaskCompletion.CompletionTask;
			GC.KeepAlive(this);
			return completionTask;
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
