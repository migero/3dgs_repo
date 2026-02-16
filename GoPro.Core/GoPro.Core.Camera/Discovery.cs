using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using camera;
using common;
using std;

namespace GoPro.Core.Camera
{
	public class Discovery
	{
		public unsafe static List<Info> FindAllCameras()
		{
			//IL_0023: Expected I, but got I8
			//IL_0029: Expected I, but got I8
			//IL_004c: Expected I, but got I8
			System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			List<Info> list;
			try
			{
				System.Runtime.CompilerServices.Unsafe.SkipInit(out vector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E obj);
				_003CModule_003E.camera_002EDiscovery_002EfindAllInterfaces(&obj, &error);
				try
				{
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					list = new List<Info>();
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
				}
				catch
				{
					//try-fault
					_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<vector<camera::Descriptor,std::allocator<camera::Descriptor> >*, void>*/)(&_003CModule_003E.std_002Evector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E_002E_007Bdtor_007D), &obj);
					throw;
				}
				_003CModule_003E.std_002Evector_003Ccamera_003A_003ADescriptor_002Cstd_003A_003Aallocator_003Ccamera_003A_003ADescriptor_003E_0020_003E_002E_Tidy(&obj);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<common.Error*, void>*/)(&_003CModule_003E.common_002EError_002E_007Bdtor_007D), &error);
				throw;
			}
			_003CModule_003E.common_002EError_002E_007Bdtor_007D(&error);
			return list;
		}
	}
}
