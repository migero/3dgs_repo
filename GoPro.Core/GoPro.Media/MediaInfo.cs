using System;
using System.Runtime.CompilerServices;
using common;
using common.http;
using common.io;
using media;
using media.gumi;
using std;
using std.filesystem;

namespace GoPro.Media
{
	public class MediaInfo
	{
		public unsafe static string Gumi(IntPtr seekablePtr)
		{
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			string result;
			try
			{
				result = _003CModule_003E.GoPro_002EMedia_002EcalculateGumi(&error, (Seekable*)seekablePtr.ToPointer());
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}

		public unsafe static string Gumi(string clrUrl)
		{
			//Discarded unreachable code: IL_00df
			//IL_0037: Expected I4, but got I8
			//IL_005c: Expected I, but got I8
			uint num = 0u;
			if (!(clrUrl == null) && clrUrl.Length != 0)
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				string result;
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
					_003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &clrUrl);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out Config config);
						// IL initblk instruction
						System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref config, 0, 36);
						System.Runtime.CompilerServices.Unsafe.As<Config, sbyte>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref config, 32)) = 0;
						System.Runtime.CompilerServices.Unsafe.SkipInit(out Session session);
						_003CModule_003E.common_002Ehttp_002ESession_002E_007Bctor_007D(&session, &error, &config);
						try
						{
							System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccommon_003A_003Aio_003A_003ASeekable_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003ASeekable_003E_0020_003E obj2);
							_003CModule_003E.common_002Eio_002ESeekable_002Ecreate(&obj2, &error, &obj, &session);
							try
							{
								Seekable* io = (Seekable*)(*(ulong*)(&obj2));
								result = _003CModule_003E.GoPro_002EMedia_002EcalculateGumi(&error, io);
							}
							catch
							{
								//try-fault
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<common::io::Seekable,std::default_delete<common::io::Seekable> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Aio_003A_003ASeekable_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003ASeekable_003E_0020_003E_002E_007Bdtor_007D), &obj2);
								throw;
							}
							_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Aio_003A_003ASeekable_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003ASeekable_003E_0020_003E_002E_007Bdtor_007D(&obj2);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Session*, void>*/)(&_003CModule_003E.common_002Ehttp_002ESession_002E_007Bdtor_007D), &session);
							throw;
						}
						_003CModule_003E.common_002Ehttp_002ESession_002E_007Bdtor_007D(&session);
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
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
					throw;
				}
				_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
				return result;
			}
			throw new ArgumentException("invalid path");
		}

		public unsafe static string MerkleGumiFromGumis(string[] clrGumis)
		{
			//Discarded unreachable code: IL_018a, IL_019d
			string text = null;
			uint num = 0u;
			if (clrGumis != null && clrGumis.Length != 0)
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out vector_003Cmedia_003A_003Agumi_003A_003AGumi_002Cstd_003A_003Aallocator_003Cmedia_003A_003Agumi_003A_003AGumi_003E_0020_003E obj);
				_003CModule_003E.std_002Evector_003Cmedia_003A_003Agumi_003A_003AGumi_002Cstd_003A_003Aallocator_003Cmedia_003A_003Agumi_003A_003AGumi_003E_0020_003E_002E_007Bctor_007D(&obj);
				string result;
				try
				{
					_003CModule_003E.std_002Evector_003Cmedia_003A_003Agumi_003A_003AGumi_002Cstd_003A_003Aallocator_003Cmedia_003A_003Agumi_003A_003AGumi_003E_0020_003E_002Ereserve(&obj, (ulong)clrGumis.LongLength);
					int num2 = 0;
					if (0L < (long)(IntPtr)(void*)clrGumis.LongLength)
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
						System.Runtime.CompilerServices.Unsafe.SkipInit(out Gumi gumi);
						do
						{
							text = clrGumis[num2];
							if (!(text == null) && text.Length != 0)
							{
								basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* ptr = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj2, &text);
								try
								{
									_003CModule_003E.media_002Egumi_002EGumi_002E_007Bctor_007D(&gumi, ptr);
									try
									{
										_003CModule_003E.std_002Evector_003Cmedia_003A_003Agumi_003A_003AGumi_002Cstd_003A_003Aallocator_003Cmedia_003A_003Agumi_003A_003AGumi_003E_0020_003E_002E_Emplace_one_at_back_003Cclass_0020media_003A_003Agumi_003A_003AGumi_003E(&obj, &gumi);
									}
									catch
									{
										//try-fault
										_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Gumi*, void>*/)(&_003CModule_003E.media_002Egumi_002EGumi_002E_007Bdtor_007D), &gumi);
										throw;
									}
									try
									{
										_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)(&gumi));
									}
									catch
									{
										//try-fault
										_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &gumi);
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
								num2++;
								continue;
							}
							throw new ArgumentException("invalid gumi");
						}
						while ((long)num2 < (long)(IntPtr)(void*)clrGumis.LongLength);
					}
					System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
					_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out Gumi gumi2);
						_003CModule_003E.media_002Egumi_002ECalculator_002EcalculateMerkle(&gumi2, &error, &obj);
						try
						{
							_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
							System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
							basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.media_002Egumi_002EGumi_002Estring(&gumi2, &obj3);
							try
							{
								result = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E(from_obj);
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
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Gumi*, void>*/)(&_003CModule_003E.media_002Egumi_002EGumi_002E_007Bdtor_007D), &gumi2);
							throw;
						}
						try
						{
							_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)(&gumi2));
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &gumi2);
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
						throw;
					}
					_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<vector<media::gumi::Gumi,std::allocator<media::gumi::Gumi> >*, void>*/)(&_003CModule_003E.std_002Evector_003Cmedia_003A_003Agumi_003A_003AGumi_002Cstd_003A_003Aallocator_003Cmedia_003A_003Agumi_003A_003AGumi_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				_003CModule_003E.std_002Evector_003Cmedia_003A_003Agumi_003A_003AGumi_002Cstd_003A_003Aallocator_003Cmedia_003A_003Agumi_003A_003AGumi_003E_0020_003E_002E_Tidy(&obj);
				return result;
			}
			throw new ArgumentException("invalid gumis");
		}

		public unsafe static DateTimeOffset CaptureTime(IntPtr seekablePtr, ValueType defaultTimezoneOffset)
		{
			System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			DateTimeOffset result;
			try
			{
				Seekable* ptr = (Seekable*)seekablePtr.ToPointer();
				System.Runtime.CompilerServices.Unsafe.SkipInit(out CaptureTime captureTime);
				_003CModule_003E.media_002ECaptureTime_002E_007Bctor_007D(&captureTime, &error, ptr);
				double totalMinutes = ((TimeSpan)defaultTimezoneOffset).TotalMinutes;
				_003CModule_003E.GoPro_002EMedia_002EfixupTimezoneOffset(&captureTime, (long)totalMinutes);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.DateTime dateTime);
				_003CModule_003E.media_002ECaptureTime_002Edate(&captureTime, &dateTime, &error);
				_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* from_obj = _003CModule_003E.common_002EDateTime_002Eiso8601WithFractionalSeconds(&dateTime, &obj);
				try
				{
					result = DateTimeOffset.Parse(_003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E(from_obj));
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
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}

		public unsafe static FrameRateData FrameRate(IntPtr seekablePtr)
		{
			if (seekablePtr == IntPtr.Zero)
			{
				throw new ArgumentException("invalid seekablePtr");
			}
			System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			FrameRateData result;
			try
			{
				Seekable* ptr = (Seekable*)seekablePtr.ToPointer();
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E obj);
				_003CModule_003E.media_002EContainer_002Efactory(&obj, &error, ptr);
				try
				{
					result = _003CModule_003E.GoPro_002EMedia_002EgetFrameRate(&error, &obj);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::Container,std::default_delete<media::Container> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D(&obj);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}

		public unsafe static FrameRateData FrameRate(string filePath)
		{
			//Discarded unreachable code: IL_010c
			//IL_0036: Expected I4, but got I8
			uint num = 0u;
			if (!(filePath == null) && filePath.Length != 0)
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				FrameRateData result;
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
					_003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &filePath);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out _Normal_conversion tag);
						// IL initblk instruction
						System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref tag, 0, 1);
						System.Runtime.CompilerServices.Unsafe.SkipInit(out path path);
						_003CModule_003E.std_002Efilesystem_002E_Convert_Source_to_wide_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstruct_0020std_003A_003Afilesystem_003A_003A_Normal_conversion_003E((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path), &obj, tag);
						System.Runtime.CompilerServices.Unsafe.SkipInit(out File file);
						try
						{
							_003CModule_003E.common_002Eio_002EFile_002E_007Bctor_007D(&file, &error, &path, (Mode)0);
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
							System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E obj2);
							_003CModule_003E.media_002EContainer_002Efactory(&obj2, &error, (Seekable*)(&file));
							try
							{
								result = _003CModule_003E.GoPro_002EMedia_002EgetFrameRate(&error, &obj2);
							}
							catch
							{
								//try-fault
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::Container,std::default_delete<media::Container> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D), &obj2);
								throw;
							}
							_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D(&obj2);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<File*, void>*/)(&_003CModule_003E.common_002Eio_002EFile_002E_007Bdtor_007D), &file);
							throw;
						}
						_003CModule_003E.common_002Eio_002EFile_002E_007Bdtor_007D(&file);
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
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
					throw;
				}
				_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
				return result;
			}
			throw new ArgumentException("invalid path");
		}

		public unsafe static Hilight[] Hilights(IntPtr seekablePtr)
		{
			if (seekablePtr == IntPtr.Zero)
			{
				throw new ArgumentException("invalid seekablePtr");
			}
			System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			Hilight[] result;
			try
			{
				Seekable* ptr = (Seekable*)seekablePtr.ToPointer();
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E obj);
				_003CModule_003E.media_002EContainer_002Efactory(&obj, &error, ptr);
				try
				{
					result = _003CModule_003E.GoPro_002EMedia_002EgetHighlights(&error, &obj);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::Container,std::default_delete<media::Container> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D(&obj);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}

		public unsafe static Hilight[] Hilights(string filePath)
		{
			//Discarded unreachable code: IL_018d
			//IL_0036: Expected I4, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
			Hilight[] result;
			if (!(filePath == null) && filePath.Length != 0)
			{
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out File file);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E obj2);
				try
				{
					_003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &filePath);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out _Normal_conversion tag);
						// IL initblk instruction
						System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref tag, 0, 1);
						System.Runtime.CompilerServices.Unsafe.SkipInit(out path path);
						_003CModule_003E.std_002Efilesystem_002E_Convert_Source_to_wide_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstruct_0020std_003A_003Afilesystem_003A_003A_Normal_conversion_003E((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path), &obj, tag);
						try
						{
							_003CModule_003E.common_002Eio_002EFile_002E_007Bctor_007D(&file, &error, &path, (Mode)0);
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
							_003CModule_003E.media_002EContainer_002Efactory(&obj2, &error, (Seekable*)(&file));
							try
							{
								if ((byte)((*(int*)(&error) != 0) ? 1u : 0u) != 0)
								{
									result = null;
									goto IL_00a9;
								}
							}
							catch
							{
								//try-fault
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::Container,std::default_delete<media::Container> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D), &obj2);
								throw;
							}
							goto end_IL_0065;
							IL_00a9:
							_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D(&obj2);
							goto IL_00c0;
							end_IL_0065:;
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<File*, void>*/)(&_003CModule_003E.common_002Eio_002EFile_002E_007Bdtor_007D), &file);
							throw;
						}
						goto end_IL_002c;
						IL_00c0:
						_003CModule_003E.common_002Eio_002EFile_002E_007Bdtor_007D(&file);
						goto IL_00d7;
						end_IL_002c:;
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj);
						throw;
					}
					goto end_IL_0022;
					IL_00d7:
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
					goto IL_00ff;
					end_IL_0022:;
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
					throw;
				}
				Hilight[] result2;
				try
				{
					try
					{
						try
						{
							try
							{
								result2 = _003CModule_003E.GoPro_002EMedia_002EgetHighlights(&error, &obj2);
							}
							catch
							{
								//try-fault
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::Container,std::default_delete<media::Container> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D), &obj2);
								throw;
							}
							_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E_002E_007Bdtor_007D(&obj2);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<File*, void>*/)(&_003CModule_003E.common_002Eio_002EFile_002E_007Bdtor_007D), &file);
							throw;
						}
						_003CModule_003E.common_002Eio_002EFile_002E_007Bdtor_007D(&file);
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
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
					throw;
				}
				_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
				return result2;
			}
			throw new ArgumentException("invalid path");
			IL_00ff:
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}

		public unsafe static Container Container(IntPtr seekablePtr)
		{
			//Discarded unreachable code: IL_003e, IL_0050
			System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			Container result;
			try
			{
				Seekable* ptr = (Seekable*)seekablePtr.ToPointer();
				if (ptr == null)
				{
					throw new OutOfMemoryException("common::io::Seekable");
				}
				result = new Container(ptr);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return result;
		}
	}
}
