using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using camera;
using common;
using common.system;
using msclr;
using std;

namespace GoPro.Core.Camera
{
	public class CameraWatcher : IDisposable
	{
		private EventHandler<Info> _003Cbacking_store_003EOnCameraAdded;

		private EventHandler<Info> _003Cbacking_store_003EOnCameraRemoved;

		private EventHandler<Info> _003Cbacking_store_003EOnCameraUpdated;

		private unsafe CameraWatcherCallback* mCallback;

		private unsafe camera.CameraWatcher* mCoreWatcher;

		private CameraChangedDelegate mCameraChangedDelegate;

		private CameraUpdatedDelegate mCameraUpdatedDelegate;

		private object mCameraListLock;

		private List<Info> mCurrentCameraSet;

		public List<Info> Cameras => mCurrentCameraSet;

		[SpecialName]
		public event EventHandler<Info> OnCameraUpdated
		{
			[MethodImpl(MethodImplOptions.Synchronized)]
			add
			{
				_003Cbacking_store_003EOnCameraUpdated = (EventHandler<Info>)Delegate.Combine(_003Cbacking_store_003EOnCameraUpdated, value);
				GC.KeepAlive(this);
			}
			[MethodImpl(MethodImplOptions.Synchronized)]
			remove
			{
				_003Cbacking_store_003EOnCameraUpdated = (EventHandler<Info>)Delegate.Remove(_003Cbacking_store_003EOnCameraUpdated, value);
				GC.KeepAlive(this);
			}
		}

		[SpecialName]
		public event EventHandler<Info> OnCameraRemoved
		{
			[MethodImpl(MethodImplOptions.Synchronized)]
			add
			{
				_003Cbacking_store_003EOnCameraRemoved = (EventHandler<Info>)Delegate.Combine(_003Cbacking_store_003EOnCameraRemoved, value);
				GC.KeepAlive(this);
			}
			[MethodImpl(MethodImplOptions.Synchronized)]
			remove
			{
				_003Cbacking_store_003EOnCameraRemoved = (EventHandler<Info>)Delegate.Remove(_003Cbacking_store_003EOnCameraRemoved, value);
				GC.KeepAlive(this);
			}
		}

		[SpecialName]
		public event EventHandler<Info> OnCameraAdded
		{
			[MethodImpl(MethodImplOptions.Synchronized)]
			add
			{
				_003Cbacking_store_003EOnCameraAdded = (EventHandler<Info>)Delegate.Combine(_003Cbacking_store_003EOnCameraAdded, value);
				GC.KeepAlive(this);
			}
			[MethodImpl(MethodImplOptions.Synchronized)]
			remove
			{
				_003Cbacking_store_003EOnCameraAdded = (EventHandler<Info>)Delegate.Remove(_003Cbacking_store_003EOnCameraAdded, value);
				GC.KeepAlive(this);
			}
		}

		[SpecialName]
		protected void raise_OnCameraAdded(object value0, Info value1)
		{
			_003Cbacking_store_003EOnCameraAdded?.Invoke(value0, value1);
		}

		[SpecialName]
		protected void raise_OnCameraRemoved(object value0, Info value1)
		{
			_003Cbacking_store_003EOnCameraRemoved?.Invoke(value0, value1);
		}

		[SpecialName]
		protected void raise_OnCameraUpdated(object value0, Info value1)
		{
			_003Cbacking_store_003EOnCameraUpdated?.Invoke(value0, value1);
		}

		public unsafe CameraWatcher()
		{
			//IL_014f: Expected I8, but got I
			//IL_0181: Expected I8, but got I
			//IL_018b: Expected I, but got I8
			//IL_0299: Expected I, but got I8
			//IL_02a4: Expected I, but got I8
			//IL_02ab: Expected I, but got I8
			//IL_02ce: Expected I, but got I8
			//IL_02de: Expected I, but got I8
			//IL_02ee: Expected I, but got I8
			//IL_0339: Expected I, but got I8
			//IL_035a: Expected I, but got I8
			uint num = 0u;
			mCameraListLock = new object();
			base._002Ector();
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003CGoPro_003A_003ACore_003A_003ACamera_003A_003ACameraWatcherCallback_002Cstd_003A_003Adefault_delete_003CGoPro_003A_003ACore_003A_003ACamera_003A_003ACameraWatcherCallback_003E_0020_003E obj);
				_003CModule_003E.std_002Emake_unique_003Cclass_0020GoPro_003A_003ACore_003A_003ACamera_003A_003ACameraWatcherCallback_002Cstruct_0020common_003A_003AError_0020_0026_002C0_003E(&obj, &error);
				try
				{
					if (*(long*)(&obj) == 0)
					{
						System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation);
						SourceLocation* pThis = &sourceLocation;
						System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj2);
						_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj2, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0O_0040HPKHPCIA_0040CameraWatcher_0040));
						try
						{
							System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj3);
							_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj3, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IK_0040MPALBPAJ_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
							try
							{
								SourceLocation* location = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation, &obj3, &obj2, 101u);
								System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj4);
								common.ErrorCode errorCode;
								try
								{
									_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj4, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CJ_0040NDNDMDPH_0040failed_003F5to_003F5allocate_003F5CameraWatche_0040));
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
					UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<vector<camera::Descriptor,std::allocator<camera::Descriptor> >*, void>*/ delegate_002A = (UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<vector<camera::Descriptor,std::allocator<camera::Descriptor> >*, void>*/)Marshal.GetFunctionPointerForDelegate(mCameraChangedDelegate = notifyCamerasChanged).ToPointer();
					*(long*)(*(long*)(&obj) + 8) = (long)(IntPtr)(void*)(ulong)delegate_002A;
					UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<vector<camera::Descriptor,std::allocator<camera::Descriptor> >*, void>*/ delegate_002A2 = (UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<vector<camera::Descriptor,std::allocator<camera::Descriptor> >*, void>*/)Marshal.GetFunctionPointerForDelegate(mCameraUpdatedDelegate = notifyCamerasUpdated).ToPointer();
					*(long*)(*(long*)(&obj) + 16) = (long)(IntPtr)(void*)(ulong)delegate_002A2;
					EventMonitor* ptr = (EventMonitor*)(*(ulong*)(*(long*)(&obj) + 24));
					System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccamera_003A_003ACameraWatcher_002Cstd_003A_003Adefault_delete_003Ccamera_003A_003ACameraWatcher_003E_0020_003E obj5);
					_003CModule_003E.std_002Emake_unique_003Cclass_0020camera_003A_003ACameraWatcher_002Cstruct_0020common_003A_003AError_0020_0026_002Cclass_0020common_003A_003Asystem_003A_003AEventMonitor_0020_002A_002C0_003E(&obj5, &error, &ptr);
					try
					{
						if (*(long*)(&obj5) == 0)
						{
							System.Runtime.CompilerServices.Unsafe.SkipInit(out SourceLocation sourceLocation2);
							SourceLocation* pThis2 = &sourceLocation2;
							System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj6);
							_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj6, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0O_0040HPKHPCIA_0040CameraWatcher_0040));
							try
							{
								System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj7);
								_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj7, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0IK_0040MPALBPAJ_0040C_003F3_003F2a_003F2_temp_003F2WorkflowOutput_003F2goop_003F9_0040));
								try
								{
									SourceLocation* location2 = _003CModule_003E.common_002ESourceLocation_002Ecurrent(&sourceLocation2, &obj7, &obj6, 117u);
									System.Runtime.CompilerServices.Unsafe.SkipInit(out basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E obj8);
									common.ErrorCode errorCode2;
									try
									{
										_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_007Bctor_007D(&obj8, (sbyte*)System.Runtime.CompilerServices.Unsafe.AsPointer(ref _003CModule_003E._003F_003F_C_0040_0CJ_0040LDNMFCHA_0040failed_003F5to_003F5allocate_003F5camera_003F3_003F3Came_0040));
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
						System.Runtime.CompilerServices.Unsafe.SkipInit(out vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E obj9);
						_003CModule_003E.camera_002ECameraWatcher_002EgetConnectedCameras((camera.CameraWatcher*)(*(ulong*)(&obj5)), &obj9);
						try
						{
							List<Info> list = new List<Info>();
							Descriptor* ptr2 = (Descriptor*)(*(ulong*)(&obj9));
							Descriptor* ptr3 = (Descriptor*)System.Runtime.CompilerServices.Unsafe.As<vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E, ulong>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref obj9, 8));
							if (*(long*)(&obj9) != System.Runtime.CompilerServices.Unsafe.As<vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E, long>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref obj9, 8)))
							{
								do
								{
									Info item = new Info(ptr2);
									list.Add(item);
									ptr2 = (Descriptor*)((long)(IntPtr)ptr2 + 240);
								}
								while (ptr2 != ptr3);
							}
							mCurrentCameraSet = list;
							CameraWatcherCallback* ptr4 = (CameraWatcherCallback*)(*(ulong*)(&obj));
							*(long*)(&obj) = 0L;
							mCallback = ptr4;
							camera.CameraWatcher* ptr5 = (camera.CameraWatcher*)(*(ulong*)(&obj5));
							*(long*)(&obj5) = 0L;
							mCoreWatcher = ptr5;
							_003CModule_003E.camera_002ECameraWatcher_002EsetCallback(ptr5, (ICameraWatcherCallback*)ptr4);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<vector<camera::Descriptor,std::allocator<camera::Descriptor> >*, void>*/)(&_003CModule_003E.std_002Evector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E_002E_007Bdtor_007D), &obj9);
							throw;
						}
						_003CModule_003E.std_002Evector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E_002E_Tidy(&obj9);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<camera::CameraWatcher,std::default_delete<camera::CameraWatcher> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccamera_003A_003ACameraWatcher_002Cstd_003A_003Adefault_delete_003Ccamera_003A_003ACameraWatcher_003E_0020_003E_002E_007Bdtor_007D), &obj5);
						throw;
					}
					if (*(long*)(&obj5) != 0L)
					{
						_003CModule_003E.std_002Edefault_delete_003Ccamera_003A_003ACameraWatcher_003E_002E_0028_0029((default_delete_003Ccamera_003A_003ACameraWatcher_003E*)(&obj5), (camera.CameraWatcher*)(*(ulong*)(&obj5)));
					}
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<GoPro::Core::Camera::CameraWatcherCallback,std::default_delete<GoPro::Core::Camera::CameraWatcherCallback> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003CGoPro_003A_003ACore_003A_003ACamera_003A_003ACameraWatcherCallback_002Cstd_003A_003Adefault_delete_003CGoPro_003A_003ACore_003A_003ACamera_003A_003ACameraWatcherCallback_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				if (*(long*)(&obj) != 0L)
				{
					_003CModule_003E.std_002Edefault_delete_003CGoPro_003A_003ACore_003A_003ACamera_003A_003ACameraWatcherCallback_003E_002E_0028_0029((default_delete_003CGoPro_003A_003ACore_003A_003ACamera_003A_003ACameraWatcherCallback_003E*)(&obj), (CameraWatcherCallback*)(*(ulong*)(&obj)));
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
		}

		private unsafe void _007ECameraWatcher()
		{
			//IL_0012: Expected I, but got I8
			//IL_0051: Expected I, but got I8
			//IL_005a: Expected I, but got I8
			//IL_0070: Expected I, but got I8
			//IL_0079: Expected I, but got I8
			camera.CameraWatcher* ptr = mCoreWatcher;
			if (ptr != null)
			{
				_003CModule_003E.camera_002ECameraWatcher_002EsetCallback(ptr, null);
				*(long*)((long)(IntPtr)mCallback + 16) = 0L;
				*(long*)((long)(IntPtr)mCallback + 8) = 0L;
				mCameraChangedDelegate = null;
				mCameraUpdatedDelegate = null;
				camera.CameraWatcher* ptr2 = mCoreWatcher;
				if (ptr2 != null)
				{
					long num = *(long*)(*(ulong*)ptr2);
					((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num)((IntPtr)ptr2, 1u);
				}
				mCoreWatcher = null;
				CameraWatcherCallback* ptr3 = mCallback;
				if (ptr3 != null)
				{
					long num2 = *(long*)(*(ulong*)ptr3);
					((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num2)((IntPtr)ptr3, 1u);
				}
				mCallback = null;
			}
		}

		public unsafe List<Info> GetConnectedCameras()
		{
			//IL_0018: Expected I, but got I8
			//IL_001e: Expected I, but got I8
			//IL_003f: Expected I, but got I8
			List<Info> list = new List<Info>();
			System.Runtime.CompilerServices.Unsafe.SkipInit(out vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E obj);
			_003CModule_003E.camera_002ECameraWatcher_002EgetConnectedCameras(mCoreWatcher, &obj);
			try
			{
				Descriptor* ptr = (Descriptor*)(*(ulong*)(&obj));
				Descriptor* ptr2 = (Descriptor*)System.Runtime.CompilerServices.Unsafe.As<vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E, ulong>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref obj, 8));
				if (*(long*)(&obj) != System.Runtime.CompilerServices.Unsafe.As<vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E, long>(ref System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref obj, 8)))
				{
					do
					{
						Info item = new Info(ptr);
						list.Add(item);
						ptr = (Descriptor*)((long)(IntPtr)ptr + 240);
					}
					while (ptr != ptr2);
				}
				GC.KeepAlive(this);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<vector<camera::Descriptor,std::allocator<camera::Descriptor> >*, void>*/)(&_003CModule_003E.std_002Evector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
			_003CModule_003E.std_002Evector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E_002E_Tidy(&obj);
			return list;
		}

		private unsafe void notifyCamerasChanged(vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E* cameras)
		{
			//IL_0021: Expected I, but got I8
			//IL_0028: Expected I, but got I8
			//IL_0046: Expected I, but got I8
			@lock @lock = null;
			@lock lock2 = new @lock(mCameraListLock);
			try
			{
				@lock = lock2;
				List<Info> list = new List<Info>();
				List<Info> list2 = new List<Info>();
				Descriptor* ptr = (Descriptor*)(*(ulong*)cameras);
				Descriptor* ptr2 = (Descriptor*)(*(ulong*)((long)(IntPtr)cameras + 8));
				if (ptr != ptr2)
				{
					do
					{
						Info item = new Info(ptr);
						list2.Add(item);
						ptr = (Descriptor*)((long)(IntPtr)ptr + 240);
					}
					while (ptr != ptr2);
				}
				bool flag = false;
				int count = mCurrentCameraSet.Count;
				if (list2.Count >= count)
				{
					flag = true;
					List<Info>.Enumerator enumerator = list2.GetEnumerator();
					if (enumerator.MoveNext())
					{
						do
						{
							Info current = enumerator.Current;
							List<Info>.Enumerator enumerator2 = mCurrentCameraSet.GetEnumerator();
							if (!enumerator2.MoveNext())
							{
								goto IL_00c2;
							}
							while (true)
							{
								string serialNumber = enumerator2.Current.SerialNumber;
								if (current.SerialNumber == serialNumber)
								{
									break;
								}
								if (enumerator2.MoveNext())
								{
									continue;
								}
								goto IL_00c2;
							}
							continue;
							IL_00c2:
							list.Add(current);
						}
						while (enumerator.MoveNext());
					}
				}
				else
				{
					List<Info>.Enumerator enumerator3 = mCurrentCameraSet.GetEnumerator();
					if (enumerator3.MoveNext())
					{
						do
						{
							Info current2 = enumerator3.Current;
							List<Info>.Enumerator enumerator4 = list2.GetEnumerator();
							if (!enumerator4.MoveNext())
							{
								goto IL_012c;
							}
							while (true)
							{
								string serialNumber2 = enumerator4.Current.SerialNumber;
								if (current2.SerialNumber == serialNumber2)
								{
									break;
								}
								if (enumerator4.MoveNext())
								{
									continue;
								}
								goto IL_012c;
							}
							continue;
							IL_012c:
							list.Add(current2);
						}
						while (enumerator3.MoveNext());
					}
				}
				if (list.Count != 0)
				{
					mCurrentCameraSet = list2;
					@lock.release();
					SendConnectionNotification(flag, list);
				}
				else if (flag)
				{
					List<Info>.Enumerator enumerator5 = list2.GetEnumerator();
					if (enumerator5.MoveNext())
					{
						do
						{
							Info current3 = enumerator5.Current;
							List<Info>.Enumerator enumerator6 = mCurrentCameraSet.GetEnumerator();
							if (!enumerator6.MoveNext())
							{
								goto IL_01bb;
							}
							while (true)
							{
								Info current4 = enumerator6.Current;
								if (current3.SdCardState == current4.SdCardState)
								{
									break;
								}
								if (enumerator6.MoveNext())
								{
									continue;
								}
								goto IL_01bb;
							}
							continue;
							IL_01bb:
							list.Add(current3);
						}
						while (enumerator5.MoveNext());
					}
					mCurrentCameraSet = list2;
					if (list.Count != 0)
					{
						@lock.release();
						SendUpdateNotification(list);
					}
				}
			}
			catch
			{
				//try-fault
				((IDisposable)@lock).Dispose();
				throw;
			}
			((IDisposable)@lock).Dispose();
		}

		private unsafe void notifyCamerasUpdated(vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E* cameras)
		{
			//IL_0009: Expected I, but got I8
			//IL_000f: Expected I, but got I8
			//IL_002a: Expected I, but got I8
			List<Info> list = new List<Info>();
			Descriptor* ptr = (Descriptor*)(*(ulong*)cameras);
			Descriptor* ptr2 = (Descriptor*)(*(ulong*)((long)(IntPtr)cameras + 8));
			if (ptr != ptr2)
			{
				do
				{
					Info item = new Info(ptr);
					list.Add(item);
					ptr = (Descriptor*)((long)(IntPtr)ptr + 240);
				}
				while (ptr != ptr2);
			}
			SendUpdateNotification(list);
		}

		private void SendConnectionNotification([MarshalAs(UnmanagedType.U1)] bool added, List<Info> cameras)
		{
			List<Info>.Enumerator enumerator = cameras.GetEnumerator();
			if (!enumerator.MoveNext())
			{
				return;
			}
			do
			{
				Info current = enumerator.Current;
				if (added)
				{
					_003Cbacking_store_003EOnCameraAdded?.Invoke(this, current);
				}
				else
				{
					_003Cbacking_store_003EOnCameraRemoved?.Invoke(this, current);
				}
			}
			while (enumerator.MoveNext());
		}

		private void SendUpdateNotification(List<Info> cameras)
		{
			List<Info>.Enumerator enumerator = cameras.GetEnumerator();
			if (enumerator.MoveNext())
			{
				do
				{
					Info current = enumerator.Current;
					_003Cbacking_store_003EOnCameraUpdated?.Invoke(this, current);
				}
				while (enumerator.MoveNext());
			}
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007ECameraWatcher();
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
