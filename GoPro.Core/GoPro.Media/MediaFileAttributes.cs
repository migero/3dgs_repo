using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using common;
using media.model;
using std;
using std.filesystem;

namespace GoPro.Media
{
	public class MediaFileAttributes : IDisposable
	{
		private unsafe media.model.MediaFileAttributes* mAttributes;

		public unsafe string SessionId
		{
			get
			{
				//IL_000f: Expected I, but got I8
				string result = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)mAttributes + 72));
				GC.KeepAlive(this);
				return result;
			}
		}

		public unsafe string LetterGroupId
		{
			get
			{
				//IL_000f: Expected I, but got I8
				string result = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020System_003A_003AString_0020_005E_002Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_0020_003E((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)((long)(IntPtr)mAttributes + 40));
				GC.KeepAlive(this);
				return result;
			}
		}

		public unsafe int ChapterId => *(int*)((long)(IntPtr)mAttributes + 32);

		public unsafe int GroupId => *(int*)((long)(IntPtr)mAttributes + 28);

		public unsafe int FolderId => *(int*)((long)(IntPtr)mAttributes + 24);

		public unsafe int ItemId => *(int*)((long)(IntPtr)mAttributes + 20);

		public unsafe int FileId => *(int*)((long)(IntPtr)mAttributes + 16);

		public unsafe int Group
		{
			get
			{
				int result = _003CModule_003E.media_002Emodel_002EMediaFileAttributes_002Egroup(mAttributes);
				GC.KeepAlive(this);
				return result;
			}
		}

		public unsafe int Item
		{
			get
			{
				int result = _003CModule_003E.media_002Emodel_002EMediaFileAttributes_002Eitem(mAttributes);
				GC.KeepAlive(this);
				return result;
			}
		}

		public unsafe ContainerFormat ContainerFormat => *(ContainerFormat*)((long)(IntPtr)mAttributes + 12);

		public unsafe MediaQuality MediaQuality => *(MediaQuality*)((long)(IntPtr)mAttributes + 8);

		public unsafe PointOfView PointOfView => *(PointOfView*)((long)(IntPtr)mAttributes + 4);

		public unsafe OptionMode OptionMode => *(OptionMode*)mAttributes;

		public unsafe bool Empty
		{
			[return: MarshalAs(UnmanagedType.U1)]
			get
			{
				bool result = _003CModule_003E.media_002Emodel_002EMediaFileAttributes_002Eempty(mAttributes);
				GC.KeepAlive(this);
				return result;
			}
		}

		public unsafe MediaFileAttributes(media.model.MediaFileAttributes* fileNameInfo)
		{
			mAttributes = fileNameInfo;
			base._002Ector();
		}

		private unsafe void _007EMediaFileAttributes()
		{
			media.model.MediaFileAttributes* ptr = mAttributes;
			if (ptr != null)
			{
				_003CModule_003E.media_002Emodel_002EMediaFileAttributes_002E__delDtor(ptr, 1u);
			}
			GC.KeepAlive(this);
		}

		public unsafe static MediaFileAttributes ParseFilename(string path)
		{
			//IL_0020: Expected I4, but got I8
			//IL_021e: Expected I, but got I8
			uint num = 0u;
			System.Runtime.CompilerServices.Unsafe.SkipInit(out Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			MediaFileAttributes result;
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj);
				basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* source = _003CModule_003E.msclr_002Einterop_002Emarshal_as_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cclass_0020System_003A_003AString_0020_005E_003E(&obj, &path);
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_003E_0020_003E obj2);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out _Normal_conversion tag);
					// IL initblk instruction
					System.Runtime.CompilerServices.Unsafe.InitBlockUnaligned(ref tag, 0, 1);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out path path2);
					_003CModule_003E.std_002Efilesystem_002E_Convert_Source_to_wide_003Cclass_0020std_003A_003Abasic_string_003Cchar_002Cstruct_0020std_003A_003Achar_traits_003Cchar_003E_002Cclass_0020std_003A_003Aallocator_003Cchar_003E_0020_003E_002Cstruct_0020std_003A_003Afilesystem_003A_003A_Normal_conversion_003E((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path2), source, tag);
					try
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out media.model.MediaFileAttributes mediaFileAttributes);
						media.model.MediaFileAttributes* _003C_Args_0_003E = _003CModule_003E.media_002Emodel_002EparseFilename(&mediaFileAttributes, &error, &path2);
						try
						{
							_003CModule_003E.std_002Emake_unique_003Cstruct_0020media_003A_003Amodel_003A_003AMediaFileAttributes_002Cstruct_0020media_003A_003Amodel_003A_003AMediaFileAttributes_002C0_003E(&obj2, _003C_Args_0_003E);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<media.model.MediaFileAttributes*, void>*/)(&_003CModule_003E.media_002Emodel_002EMediaFileAttributes_002E_007Bdtor_007D), &mediaFileAttributes);
							throw;
						}
						try
						{
							try
							{
								basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* pThis = (basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref mediaFileAttributes, 72));
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref mediaFileAttributes, 72)));
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), pThis);
									throw;
								}
							}
							catch
							{
								//try-fault
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), System.Runtime.CompilerServices.Unsafe.AsPointer(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref mediaFileAttributes, 40)));
								throw;
							}
							basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E* pThis2 = (basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref mediaFileAttributes, 40));
							try
							{
								_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref mediaFileAttributes, 40)));
							}
							catch
							{
								//try-fault
								_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), pThis2);
								throw;
							}
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::model::MediaFileAttributes,std::default_delete<media::model::MediaFileAttributes> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_003E_0020_003E_002E_007Bdtor_007D), &obj2);
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<path*, void>*/)(&_003CModule_003E.std_002Efilesystem_002Epath_002E_007Bdtor_007D), &path2);
						throw;
					}
					try
					{
						try
						{
							_003CModule_003E.std_002Ebasic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cwchar_t_002Cstd_003A_003Achar_traits_003Cwchar_t_003E_002Cstd_003A_003Aallocator_003Cwchar_t_003E_0020_003E*)(&path2));
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<wchar_t>,std::_String_val<std::_Simple_types<wchar_t> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cwchar_t_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cwchar_t_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &path2);
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::model::MediaFileAttributes,std::default_delete<media::model::MediaFileAttributes> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_003E_0020_003E_002E_007Bdtor_007D), &obj2);
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
					if (*(long*)(&obj2) == 0)
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
						SourceLocation* pThis3 = &sourceLocation;
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
						_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj3, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0O_0040MJELENGN_0040ParseFilename_0040));
						try
						{
							System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj4);
							_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj4, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IK_0040EEBOMFOP_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
							try
							{
								SourceLocation* location = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj4, &obj3, 107u);
								System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj5);
								ErrorCode errorCode;
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj5, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CH_0040CCPKOAKN_0040failed_003F5to_003F5allocate_003F5MediaFileAtt_0040));
									try
									{
										errorCode = (ErrorCode)16u;
									}
									catch
									{
										//try-fault
										_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj5);
										throw;
									}
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<SourceLocation*, void>*/)(&_003CModule_003E.common_002ESourceLocation_002E_007Bdtor_007D), pThis3);
									throw;
								}
								try
								{
									_003CModule_003E.common_002EError_002Eset_003Cenum_0020common_003A_003AErrorCode_003E(&error, &errorCode, &obj5, location);
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<basic_string<char,std::char_traits<char>,std::allocator<char> >*, void>*/)(&_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bdtor_007D), &obj5);
									throw;
								}
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate(&obj5);
								}
								catch
								{
									//try-fault
									_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &obj5);
									throw;
								}
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
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					long num2 = *(long*)(&obj2);
					*(long*)(&obj2) = 0L;
					result = new MediaFileAttributes((media.model.MediaFileAttributes*)num2);
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<media::model::MediaFileAttributes,std::default_delete<media::model::MediaFileAttributes> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_003E_0020_003E_002E_007Bdtor_007D), &obj2);
					throw;
				}
				_003CModule_003E.std_002Eunique_ptr_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003Amodel_003A_003AMediaFileAttributes_003E_0020_003E_002E_007Bdtor_007D(&obj2);
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

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007EMediaFileAttributes();
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
