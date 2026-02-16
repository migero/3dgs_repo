using System;
using System.Runtime.CompilerServices;
using common;
using common.io;
using std;

namespace GoPro.Core
{
	public class CachedSeekable : Seekable
	{
		public unsafe CachedSeekable(Seekable otherSeekable)
		{
			//IL_005c: Expected I, but got I8
			uint num = 0u;
			((object)this)._002Ector();
			try
			{
				if (otherSeekable == null)
				{
					throw new ArgumentNullException("invalid other seekable");
				}
				common.io.Seekable* ptr = (common.io.Seekable*)otherSeekable.ReleasePointer().ToPointer();
				if (ptr == null)
				{
					throw new ArgumentNullException("invalid other seekable");
				}
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				try
				{
					System.Runtime.CompilerServices.Unsafe.SkipInit(out unique_ptr_003Ccommon_003A_003Aio_003A_003ACachedSeekable_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003ACachedSeekable_003E_0020_003E obj);
					_003CModule_003E.std_002Emake_unique_003Cclass_0020common_003A_003Aio_003A_003ACachedSeekable_002Cstruct_0020common_003A_003AError_0020_0026_002Cclass_0020common_003A_003Aio_003A_003ASeekable_0020_0026_002C0_003E(&obj, &error, ptr);
					try
					{
						_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
						long num2 = *(long*)(&obj);
						*(long*)(&obj) = 0L;
						IntPtr intPtr2 = (base.Pointer = (IntPtr)(void*)num2);
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<unique_ptr<common::io::CachedSeekable,std::default_delete<common::io::CachedSeekable> >*, void>*/)(&_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Aio_003A_003ACachedSeekable_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003ACachedSeekable_003E_0020_003E_002E_007Bdtor_007D), &obj);
						throw;
					}
					_003CModule_003E.std_002Eunique_ptr_003Ccommon_003A_003Aio_003A_003ACachedSeekable_002Cstd_003A_003Adefault_delete_003Ccommon_003A_003Aio_003A_003ACachedSeekable_003E_0020_003E_002E_007Bdtor_007D(&obj);
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
