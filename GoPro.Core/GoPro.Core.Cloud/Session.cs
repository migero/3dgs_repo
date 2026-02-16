using System;
using System.Runtime.CompilerServices;
using System.Runtime.ExceptionServices;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using cloud;
using common;
using common.http;
using GoPro.Core.Http;
using std;

namespace GoPro.Core.Cloud
{
	public class Session : GoPro.Core.Http.Session
	{
		protected unsafe AuthorizationForwardingDelegate* mAuthorizationForwardingDelegate;

		public unsafe virtual string Server
		{
			get
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.cloud_002ESession_002Eserver((cloud.Session*)_003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0), &obj);
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
				void* ptr = _003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr2 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &value);
				try
				{
					_003CModule_003E.cloud_002ESession_002Eserver((cloud.Session*)ptr, ptr2);
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

		public unsafe UserAuthorizationsRefreshed OnUserAuthorizationsRefreshed
		{
			set
			{
				_003CModule_003E.GoPro_002ECore_002ECloud_002EAuthorizationForwardingDelegate_002EsetUserAuthorizationsRefreshedDelegate(mAuthorizationForwardingDelegate, value);
				GC.KeepAlive(this);
			}
		}

		public unsafe RequestClientCredentials OnRequestClientCredentials
		{
			get
			{
				//IL_000f: Expected I, but got I8
				return _003CModule_003E.gcroot_003CGoPro_003A_003ACore_003A_003ACloud_003A_003ARequestClientCredentials_0020_005E_003E_002E_002EPE_0024AAVRequestClientCredentials_0040Cloud_0040Core_0040GoPro_0040_0040((gcroot_003CGoPro_003A_003ACore_003A_003ACloud_003A_003ARequestClientCredentials_0020_005E_003E*)((long)(IntPtr)mAuthorizationForwardingDelegate + 24));
			}
			set
			{
				_003CModule_003E.GoPro_002ECore_002ECloud_002EAuthorizationForwardingDelegate_002EsetRequestClientCredentialsDelegate(mAuthorizationForwardingDelegate, value);
				GC.KeepAlive(this);
			}
		}

		public unsafe RequestUserAuthorizations OnRequestUserAuthorizations
		{
			set
			{
				_003CModule_003E.GoPro_002ECore_002ECloud_002EAuthorizationForwardingDelegate_002EsetRequestUserAuthorizationsDelegate(mAuthorizationForwardingDelegate, value);
				GC.KeepAlive(this);
			}
		}

		public unsafe RequestUserCredentials OnRequestUserCredentials
		{
			get
			{
				//IL_000e: Expected I, but got I8
				return _003CModule_003E.gcroot_003CGoPro_003A_003ACore_003A_003ACloud_003A_003ARequestUserCredentials_0020_005E_003E_002E_002EPE_0024AAVRequestUserCredentials_0040Cloud_0040Core_0040GoPro_0040_0040((gcroot_003CGoPro_003A_003ACore_003A_003ACloud_003A_003ARequestUserCredentials_0020_005E_003E*)((long)(IntPtr)mAuthorizationForwardingDelegate + 8));
			}
			set
			{
				_003CModule_003E.GoPro_002ECore_002ECloud_002EAuthorizationForwardingDelegate_002EsetRequestUserCredentialsDelegate(mAuthorizationForwardingDelegate, value);
				GC.KeepAlive(this);
			}
		}

		public unsafe Session()
		{
			//IL_000b: Expected I, but got I8
			//IL_011e: Expected I, but got I8
			//IL_021b: Expected I, but got I8
			//IL_023d: Expected I, but got I8
			//IL_0242: Expected I, but got I8
			//IL_026f: Expected I, but got I8
			//IL_0290: Expected I, but got I8
			uint num = 0u;
			mAuthorizationForwardingDelegate = null;
			base._002Ector();
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003CGoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_002Cstd_003A_003Adefault_delete_003CGoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_003E_0020_003E obj);
					_003CModule_003E.std_002Emake_unique_003Cclass_0020GoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_002C0_003E(&obj);
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
								_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj3, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0ID_0040BBPLJKFG_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
								try
								{
									SourceLocation* location = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj3, &obj2, 28u);
									System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj4);
									common.ErrorCode errorCode;
									try
									{
										_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj4, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0DD_0040BPGHBBEA_0040failed_003F5to_003F5allocate_003F5Authorizatio_0040));
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
						System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccloud_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccloud_003A_003ASession_003E_0020_003E obj5);
						_003CModule_003E.std_002Emake_unique_003Cclass_0020cloud_003A_003ASession_002Cstruct_0020common_003A_003AError_0020_0026_002Cclass_0020GoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_0020_0026_002C0_003E(&obj5, &error, (AuthorizationForwardingDelegate*)(*(ulong*)(&obj)));
						try
						{
							if (*(long*)(&obj5) == 0)
							{
								System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation2);
								SourceLocation* pThis2 = &sourceLocation2;
								System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj6);
								_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj6, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_07FFOFCADM_0040Session_0040));
								try
								{
									System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj7);
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj7, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0ID_0040BBPLJKFG_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
									try
									{
										SourceLocation* location2 = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation2, &obj7, &obj6, 31u);
										System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj8);
										common.ErrorCode errorCode2;
										try
										{
											_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj8, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CC_0040LPGIPBGL_0040failed_003F5to_003F5allocate_003F5cloud_003F3_003F3Sessi_0040));
											try
											{
												errorCode2 = (common.ErrorCode)16u;
											}
											catch
											{
												//try-fault
												_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj8);
												throw;
											}
										}
										catch
										{
											//try-fault
											_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<SourceLocation*, void>*/)(&_003CModule_003E.common_002ESourceLocation_002E_007Bdtor_007D), pThis2);
											throw;
										}
										try
										{
											_003CModule_003E.common_002EError_002Eset_003Cenum_0020common_003A_003AErrorCode_003E(&error, &errorCode2, &obj8, location2);
										}
										catch
										{
											//try-fault
											_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj8);
											throw;
										}
										try
										{
											_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj8);
										}
										catch
										{
											//try-fault
											_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj8);
											throw;
										}
									}
									catch
									{
										//try-fault
										_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj7);
										throw;
									}
									try
									{
										_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj7);
									}
									catch
									{
										//try-fault
										_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj7);
										throw;
									}
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj6);
									throw;
								}
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj6);
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj6);
									throw;
								}
							}
							_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
							AuthorizationForwardingDelegate* ptr = (AuthorizationForwardingDelegate*)(*(ulong*)(&obj));
							*(long*)(&obj) = 0L;
							mAuthorizationForwardingDelegate = ptr;
							common.http.Session* ptr2 = mSession;
							if (ptr2 != null)
							{
								long num2 = *(long*)(*(ulong*)ptr2);
								((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num2)((IntPtr)ptr2, 1u);
							}
							cloud.Session* ptr3 = (cloud.Session*)(*(ulong*)(&obj5));
							*(long*)(&obj5) = 0L;
							mSession = (common.http.Session*)ptr3;
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<cloud::Session,std::default_delete<cloud::Session> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccloud_003A_003ASession_002Cstd_003A_003Adefault_delete_003Ccloud_003A_003ASession_003E_0020_003E_002E_007Bdtor_007D), &obj5);
							throw;
						}
						if (*(long*)(&obj5) != 0L)
						{
							_003CModule_003E.std_002Edefault_delete_003Ccloud_003A_003ASession_003E_002E_0028_0029((default_delete_003Ccloud_003A_003ASession_003E*)(&obj5), (cloud.Session*)(*(ulong*)(&obj5)));
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<GoPro::Core::Cloud::AuthorizationForwardingDelegate,std::default_delete<GoPro::Core::Cloud::AuthorizationForwardingDelegate> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003CGoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_002Cstd_003A_003Adefault_delete_003CGoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_003E_0020_003E_002E_007Bdtor_007D), &obj);
						throw;
					}
					if (*(long*)(&obj) != 0L)
					{
						_003CModule_003E.std_002Edefault_delete_003CGoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_003E_002E_0028_0029((default_delete_003CGoPro_003A_003ACore_003A_003ACloud_003A_003AAuthorizationForwardingDelegate_003E*)(&obj), (AuthorizationForwardingDelegate*)(*(ulong*)(&obj)));
					}
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

		private unsafe void _007ESession()
		{
			//IL_0016: Expected I, but got I8
			AuthorizationForwardingDelegate* ptr = mAuthorizationForwardingDelegate;
			if (ptr != null)
			{
				long num = *(long*)(*(ulong*)ptr);
				((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num)((IntPtr)ptr, 1u);
			}
			GC.KeepAlive(this);
		}

		public unsafe GoPro.Core.Http.Request CreateRequest(string apiToken, params string[] parameters)
		{
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Request result;
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out vector_003Cstd_003A_003Apair_003Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E_002Cstd_003A_003Aallocator_003Cstd_003A_003Apair_003Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E_0020_003E_0020_003E obj);
				_003CModule_003E.common_002Eclr_002EConvertToKeyValuePairs(&obj, parameters);
				try
				{
					void* ptr = _003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
					basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr2 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj2, &apiToken);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request);
						common.http.Request* cppRequest = _003CModule_003E.cloud_002ESession_002EcreateRequest((cloud.Session*)ptr, &request, &error, ptr2, &obj);
						try
						{
							result = _003CModule_003E.common_002Eclr_002EConvertRequestToClr(cppRequest);
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
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					GC.KeepAlive(this);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<vector<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char> >,std::basic_string<char,std::char_traits<char>,std::allocator<char> > >,std::allocator<std::pair<std::basic_string<char,std::char_traits<char>,std::allocator<char> >,std::basic_string<char,std::char_traits<char>,std::allocator<char> > > > >*, void>*/)(&_003CModule_003E.std_002Evector_003Cstd_003A_003Apair_003Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E_002Cstd_003A_003Aallocator_003Cstd_003A_003Apair_003Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E_0020_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				_003CModule_003E.std_002Evector_003Cstd_003A_003Apair_003Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E_002Cstd_003A_003Aallocator_003Cstd_003A_003Apair_003Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstd_003A_003Abasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E_0020_003E_0020_003E_002E_Tidy(&obj);
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

		public GoPro.Core.Http.Request CreateRequest(string apiToken)
		{
			uint num = 0u;
			return CreateRequest(apiToken, (string[])null);
		}

		public unsafe GoPro.Core.Http.Request CreateThumbnailRequest(string mediumToken, int minWidth, int index)
		{
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Request result;
			try
			{
				void* ptr = _003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr2 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &mediumToken);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request);
					common.http.Request* cppRequest = _003CModule_003E.cloud_002ESession_002EcreateThumbnailRequest((cloud.Session*)ptr, &request, &error, ptr2, minWidth, index);
					try
					{
						result = _003CModule_003E.common_002Eclr_002EConvertRequestToClr(cppRequest);
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

		public GoPro.Core.Http.Request CreateThumbnailRequest(string mediumToken, int minWidth)
		{
			uint num = 0u;
			return CreateThumbnailRequest(mediumToken, minWidth, 1);
		}

		public unsafe GoPro.Core.Http.Request Handle(GoPro.Core.Http.Request request)
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
					_003CModule_003E.common_002Ehttp_002ESession_002Ehandle((common.http.Session*)_003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0), &optional_003Ccommon_003A_003Ahttp_003A_003AResponse_003E, &error, &request2);
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

		public unsafe override GoPro.Core.Http.Response Perform(GoPro.Core.Http.Request request)
		{
			//IL_0043: Expected I, but got I8
			//IL_0044: Expected I8, but got I
			//IL_004a: Expected I, but got I8
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			GoPro.Core.Http.Response result;
			try
			{
				void* ptr = _003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0);
				long num = *(long*)(*(long*)ptr + 32);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Request request2);
				common.http.Request* ptr2 = &request2;
				common.http.Request* ptr3 = _003CModule_003E.common_002Eclr_002EConvertRequestToCpp(&request2, request);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.http.Response response);
				long num2 = (long)(IntPtr)((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.http.Response*, common.Error*, common.http.Request*, common.http.Response*>*/)(void*)num)((IntPtr)ptr, &response, &error, ptr3);
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

		public unsafe void Login(string username, string password, string scopes, string twofactor)
		{
			//Discarded unreachable code: IL_010e
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			try
			{
				void* ptr = _003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr2 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &twofactor);
				cloud.LoginResult loginResult;
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
					basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr3 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj2, &scopes);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
						basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr4 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj3, &password);
						try
						{
							System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj4);
							basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr5 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj4, &username);
							try
							{
								loginResult = _003CModule_003E.cloud_002ESession_002Elogin((cloud.Session*)ptr, &error, ptr5, ptr4, ptr3, ptr2);
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
				LoginException ex = LoginException.Create(&error, loginResult);
				if (ex != null)
				{
					throw ex;
				}
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			try
			{
				return;
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
		}

		public void Login(string username, string password, string scopes)
		{
			uint num = 0u;
			Login(username, password, scopes, "");
		}

		public unsafe void Logout()
		{
			_003CModule_003E.cloud_002ESession_002Elogout((cloud.Session*)_003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0));
			GC.KeepAlive(this);
		}

		[return: MarshalAs(UnmanagedType.U1)]
		public unsafe bool LoggedIn()
		{
			bool result = _003CModule_003E.cloud_002ESession_002EloggedIn((cloud.Session*)_003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0));
			GC.KeepAlive(this);
			return result;
		}

		public unsafe Task<GoPro.Core.Http.Response> Request2FACodeAsync(string email)
		{
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			Task<GoPro.Core.Http.Response> completionTask;
			try
			{
				HttpTaskCompletion httpTaskCompletion = new HttpTaskCompletion();
				void* ptr = _003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out function_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E obj);
				function_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E* pThis = &obj;
				function_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E* ptr2 = httpTaskCompletion.get_HttpCompletion(&obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr3;
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
				try
				{
					ptr3 = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj2, &email);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<function<void __cdecl(common::Error &,common::http::Request &,common::http::Response &)>*, void>*/)(&_003CModule_003E.std_002Efunction_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E_002E_007Bdtor_007D), pThis);
					throw;
				}
				try
				{
					_003CModule_003E.cloud_002ESession_002Erequest2FACode((cloud.Session*)ptr, &error, ptr3, ptr2);
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
				_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
				completionTask = httpTaskCompletion.CompletionTask;
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
			return completionTask;
		}

		public unsafe string AccessToken()
		{
			System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
			basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.cloud_002ESession_002EaccessToken((cloud.Session*)_003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0), &obj);
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

		public unsafe IntPtr ToPointer()
		{
			IntPtr result = (IntPtr)mSession;
			GC.KeepAlive(this);
			return result;
		}

		protected unsafe cloud.Session* session()
		{
			return (cloud.Session*)_003CModule_003E.__RTDynamicCast(mSession, 0, System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040http_0040common_0040_0040_00408), System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_R0_003FAVSession_0040cloud_0040_0040_00408), 0);
		}

		[HandleProcessCorruptedStateExceptions]
		protected override void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				try
				{
					_007ESession();
					return;
				}
				finally
				{
					base.Dispose(A_0: true);
				}
			}
			base.Dispose(A_0: false);
		}
	}
}
