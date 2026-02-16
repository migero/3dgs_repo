using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using common;
using common.io;
using GoPro.Core;
using media;
using media.model;
using std;

namespace GoPro.Media
{
	public class Container : IDisposable
	{
		private unsafe media.Container* mContainer;

		public unsafe captureType CaptureType
		{
			get
			{
				//IL_0020: Expected I, but got I8
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				media.captureType result;
				try
				{
					media.Container* ptr = mContainer;
					long num = *(long*)(*(long*)ptr + 48);
					result = ((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.Error*, media.captureType>*/)(void*)num)((IntPtr)ptr, &error);
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
				return (captureType)result;
			}
		}

		public unsafe containerType ContainerType
		{
			get
			{
				//IL_0020: Expected I, but got I8
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				media.containerType result;
				try
				{
					media.Container* ptr = mContainer;
					long num = *(long*)(*(long*)ptr + 40);
					result = ((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.Error*, media.containerType>*/)(void*)num)((IntPtr)ptr, &error);
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
				return (containerType)result;
			}
		}

		public unsafe bool IsGoProMedia
		{
			[return: MarshalAs(UnmanagedType.U1)]
			get
			{
				//IL_0020: Expected I, but got I8
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				bool result;
				try
				{
					media.Container* ptr = mContainer;
					long num = *(long*)(*(long*)ptr + 56);
					result = ((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.Error*, byte>*/)(void*)num)((IntPtr)ptr, &error) != 0;
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
		}

		public unsafe GoPro.Core.CameraModel CameraModel
		{
			get
			{
				//IL_0022: Expected I, but got I8
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				GoPro.Core.CameraModel result;
				try
				{
					media.Container* ptr = mContainer;
					long num = *(long*)(*(long*)ptr + 32);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out common.CameraModel cameraModel);
					((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.CameraModel*, common.Error*, common.CameraModel*>*/)(void*)num)((IntPtr)ptr, &cameraModel, &error);
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					GC.KeepAlive(this);
					result = *(GoPro.Core.CameraModel*)(&cameraModel);
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
		}

		public unsafe GoPro.Core.FirmwareVersion FirmwareVersion
		{
			get
			{
				//IL_0022: Expected I, but got I8
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				GoPro.Core.FirmwareVersion result;
				try
				{
					media.Container* ptr = mContainer;
					long num = *(long*)(*(long*)ptr + 24);
					System.Runtime.CompilerServices.Unsafe.SkipInit(out common.FirmwareVersion firmwareVersion);
					((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.FirmwareVersion*, common.Error*, common.FirmwareVersion*>*/)(void*)num)((IntPtr)ptr, &firmwareVersion, &error);
					try
					{
						_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
						GoPro.Core.FirmwareVersion firmwareVersion2 = new GoPro.Core.FirmwareVersion(&firmwareVersion);
						result = firmwareVersion2;
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.FirmwareVersion*, void>*/)(&_003CModule_003E.common_002EFirmwareVersion_002E_007Bdtor_007D), &firmwareVersion);
						throw;
					}
					try
					{
						_003CModule_003E.std_002Ebasic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E_002E_Tidy_deallocate((basic_string_003Cchar_002Cstd_003A_003Achar_traits_003Cchar_003E_002Cstd_003A_003Aallocator_003Cchar_003E_0020_003E*)(&firmwareVersion));
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<_Compressed_pair<std::allocator<char>,std::_String_val<std::_Simple_types<char> >,1>*, void>*/)(&_003CModule_003E.std_002E_Compressed_pair_003Cstd_003A_003Aallocator_003Cchar_003E_002Cstd_003A_003A_String_val_003Cstd_003A_003A_Simple_types_003Cchar_003E_0020_003E_002C1_003E_002E_007Bdtor_007D), &firmwareVersion);
						throw;
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
				return result;
			}
		}

		public unsafe ContainerFormat Type
		{
			get
			{
				//IL_0011: Expected I, but got I8
				media.Container* intPtr = mContainer;
				media.model.ContainerFormat result = ((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, media.model.ContainerFormat>*/)(void*)(*(ulong*)(*(long*)intPtr + 8)))((IntPtr)intPtr);
				GC.KeepAlive(this);
				return (ContainerFormat)result;
			}
		}

		public unsafe Container(common.io.Seekable* io)
		{
			//IL_0024: Expected I, but got I8
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Cmedia_003A_003AContainer_002Cstd_003A_003Adefault_delete_003Cmedia_003A_003AContainer_003E_0020_003E obj);
				_003CModule_003E.media_002EContainer_002Efactory(&obj, &error, io);
				try
				{
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					media.Container* ptr = (media.Container*)(*(ulong*)(&obj));
					*(long*)(&obj) = 0L;
					mContainer = ptr;
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
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			GC.KeepAlive(this);
		}

		private unsafe void _007EContainer()
		{
			//IL_0016: Expected I, but got I8
			media.Container* ptr = mContainer;
			if (ptr != null)
			{
				long num = *(long*)(*(ulong*)ptr);
				((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num)((IntPtr)ptr, 1u);
			}
			GC.KeepAlive(this);
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007EContainer();
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
