using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using common;
using common.io;

namespace GoPro.Core
{
	public class Seekable : IDisposable
	{
		private unsafe common.io.Seekable* mIo;

		public unsafe int Size
		{
			get
			{
				//IL_0023: Expected I, but got I8
				System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
				_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
				int result;
				try
				{
					common.io.Seekable* ptr = mIo;
					long num = *(long*)(*(long*)ptr + 136);
					ulong num2 = ((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, common.Error*, ulong>*/)(void*)num)((IntPtr)ptr, &error);
					_003CModule_003E.common_002Eclr_002EThrowManagedExceptionOnError(&error);
					GC.KeepAlive(this);
					result = (int)num2;
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

		public unsafe IntPtr Pointer
		{
			get
			{
				IntPtr result = (IntPtr)mIo;
				GC.KeepAlive(this);
				return result;
			}
			protected set
			{
				mIo = (common.io.Seekable*)value.ToPointer();
				GC.KeepAlive(this);
			}
		}

		private unsafe void _007ESeekable()
		{
			//IL_0016: Expected I, but got I8
			common.io.Seekable* ptr = mIo;
			if (ptr != null)
			{
				long num = *(long*)(*(ulong*)ptr);
				((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num)((IntPtr)ptr, 1u);
			}
			GC.KeepAlive(this);
		}

		public unsafe IntPtr ReleasePointer()
		{
			//IL_000e: Expected I, but got I8
			IntPtr pointer = Pointer;
			mIo = null;
			return pointer;
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007ESeekable();
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
