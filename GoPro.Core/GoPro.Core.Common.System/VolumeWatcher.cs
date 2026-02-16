using System;
using System.Collections.Generic;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using common;
using common.system;
using std;

namespace GoPro.Core.Common.System
{
	public class VolumeWatcher : IDisposable
	{
		private EventHandler<List<VolumeData>> _003Cbacking_store_003EOnVolumesChanged;

		private unsafe VolumeWatcherCallback* mCallback;

		private unsafe common.system.VolumeWatcher* mCoreWatcher;

		private VolumeChangedDelegate mVolumeChangedDelegate;

		[SpecialName]
		public event EventHandler<List<VolumeData>> OnVolumesChanged
		{
			[MethodImpl(MethodImplOptions.Synchronized)]
			add
			{
				_003Cbacking_store_003EOnVolumesChanged = (EventHandler<List<VolumeData>>)Delegate.Combine(_003Cbacking_store_003EOnVolumesChanged, value);
				GC.KeepAlive(this);
			}
			[MethodImpl(MethodImplOptions.Synchronized)]
			remove
			{
				_003Cbacking_store_003EOnVolumesChanged = (EventHandler<List<VolumeData>>)Delegate.Remove(_003Cbacking_store_003EOnVolumesChanged, value);
				GC.KeepAlive(this);
			}
		}

		[SpecialName]
		protected void raise_OnVolumesChanged(object value0, List<VolumeData> value1)
		{
			_003Cbacking_store_003EOnVolumesChanged?.Invoke(value0, value1);
		}

		public unsafe VolumeWatcher()
		{
			//IL_0020: Expected I, but got I8
			//IL_0065: Expected I8, but got I
			//IL_0086: Expected I, but got I8
			//IL_0096: Expected I, but got I8
			VolumeWatcherCallback* ptr = (VolumeWatcherCallback*)_003CModule_003E.@new(32uL);
			VolumeWatcherCallback* ptr2;
			try
			{
				ptr2 = ((ptr == null) ? null : _003CModule_003E.GoPro_002ECore_002ECommon_002ESystem_002EVolumeWatcherCallback_002E_007Bctor_007D(ptr));
			}
			catch
			{
				//try-fault
				_003CModule_003E.delete(ptr, 32uL);
				throw;
			}
			mCallback = ptr2;
			UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<vector<common::system::VolumeData,std::allocator<common::system::VolumeData> >*, void>*/ delegate_002A = (UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<vector<common::system::VolumeData,std::allocator<common::system::VolumeData> >*, void>*/)Marshal.GetFunctionPointerForDelegate(mVolumeChangedDelegate = NotifyVolumesChanged).ToPointer();
			*(long*)((long)(IntPtr)mCallback + 8) = (long)(IntPtr)(void*)(ulong)delegate_002A;
			global::System.Runtime.CompilerServices.Unsafe.SkipInit(out common.Error error);
			_003CModule_003E.common_002EError_002E_007Bctor_007D(&error);
			try
			{
				common.system.VolumeWatcher* ptr3 = (common.system.VolumeWatcher*)_003CModule_003E.@new(48uL);
				common.system.VolumeWatcher* ptr5;
				try
				{
					if (ptr3 != null)
					{
						EventMonitor* ptr4 = (EventMonitor*)(*(ulong*)((long)(IntPtr)mCallback + 16));
						ptr5 = _003CModule_003E.common_002Esystem_002EVolumeWatcher_002E_007Bctor_007D(ptr3, &error, ptr4);
					}
					else
					{
						ptr5 = null;
					}
				}
				catch
				{
					//try-fault
					_003CModule_003E.delete(ptr3, 48uL);
					throw;
				}
				mCoreWatcher = ptr5;
				_003CModule_003E.common_002Esystem_002EVolumeWatcher_002EsetCallback(ptr5, (IVolumeWatcherCallback*)mCallback);
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

		private unsafe void _007EVolumeWatcher()
		{
			//IL_0012: Expected I, but got I8
			//IL_003d: Expected I, but got I8
			//IL_0046: Expected I, but got I8
			//IL_005c: Expected I, but got I8
			//IL_0065: Expected I, but got I8
			common.system.VolumeWatcher* ptr = mCoreWatcher;
			if (ptr != null)
			{
				_003CModule_003E.common_002Esystem_002EVolumeWatcher_002EsetCallback(ptr, null);
				*(long*)((long)(IntPtr)mCallback + 8) = 0L;
				mVolumeChangedDelegate = null;
				common.system.VolumeWatcher* ptr2 = mCoreWatcher;
				if (ptr2 != null)
				{
					long num = *(long*)(*(ulong*)ptr2);
					((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num)((IntPtr)ptr2, 1u);
				}
				mCoreWatcher = null;
				VolumeWatcherCallback* ptr3 = mCallback;
				if (ptr3 != null)
				{
					long num2 = *(long*)(*(ulong*)ptr3);
					((UIntPtr/*delegate* unmanaged[Cdecl, Cdecl]<IntPtr, uint, void*>*/)(void*)num2)((IntPtr)ptr3, 1u);
				}
				mCallback = null;
			}
		}

		public static VolumeDifference DiffVolumes(List<VolumeData> oldCollection, List<VolumeData> newCollection)
		{
			VolumeDifference volumeDifference = new VolumeDifference();
			if (newCollection.Count >= oldCollection.Count)
			{
				volumeDifference.Added = true;
				List<VolumeData>.Enumerator enumerator = newCollection.GetEnumerator();
				if (enumerator.MoveNext())
				{
					do
					{
						VolumeData current = enumerator.Current;
						List<VolumeData>.Enumerator enumerator2 = oldCollection.GetEnumerator();
						if (!enumerator2.MoveNext())
						{
							goto IL_006e;
						}
						while (true)
						{
							string volumeNumber = enumerator2.Current.VolumeNumber;
							if (current.VolumeNumber == volumeNumber)
							{
								break;
							}
							if (enumerator2.MoveNext())
							{
								continue;
							}
							goto IL_006e;
						}
						continue;
						IL_006e:
						volumeDifference.Data.Add(current);
					}
					while (enumerator.MoveNext());
				}
			}
			else
			{
				List<VolumeData>.Enumerator enumerator3 = oldCollection.GetEnumerator();
				if (enumerator3.MoveNext())
				{
					do
					{
						VolumeData current2 = enumerator3.Current;
						List<VolumeData>.Enumerator enumerator4 = newCollection.GetEnumerator();
						if (!enumerator4.MoveNext())
						{
							goto IL_00d3;
						}
						while (true)
						{
							string volumeNumber2 = enumerator4.Current.VolumeNumber;
							if (current2.VolumeNumber == volumeNumber2)
							{
								break;
							}
							if (enumerator4.MoveNext())
							{
								continue;
							}
							goto IL_00d3;
						}
						continue;
						IL_00d3:
						volumeDifference.Data.Add(current2);
					}
					while (enumerator3.MoveNext());
				}
			}
			return volumeDifference;
		}

		public unsafe List<VolumeData> GetCurrentVolumes()
		{
			//IL_0018: Expected I, but got I8
			//IL_001e: Expected I, but got I8
			//IL_003c: Expected I, but got I8
			global::System.Runtime.CompilerServices.Unsafe.SkipInit(out vector_003Ccommon_003A_003Asystem_003A_003AVolumeData_002Cstd_003A_003Aallocator_003Ccommon_003A_003Asystem_003A_003AVolumeData_003E_0020_003E obj);
			_003CModule_003E.common_002Esystem_002EVolumeWatcher_002EgetCurrentVolumes(mCoreWatcher, &obj);
			List<VolumeData> list;
			try
			{
				list = new List<VolumeData>();
				common.system.VolumeData* ptr = (common.system.VolumeData*)(*(ulong*)(&obj));
				common.system.VolumeData* ptr2 = (common.system.VolumeData*)global::System.Runtime.CompilerServices.Unsafe.As<vector_003Ccommon_003A_003Asystem_003A_003AVolumeData_002Cstd_003A_003Aallocator_003Ccommon_003A_003Asystem_003A_003AVolumeData_003E_0020_003E, ulong>(ref global::System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref obj, 8));
				if (*(long*)(&obj) != global::System.Runtime.CompilerServices.Unsafe.As<vector_003Ccommon_003A_003Asystem_003A_003AVolumeData_002Cstd_003A_003Aallocator_003Ccommon_003A_003Asystem_003A_003AVolumeData_003E_0020_003E, long>(ref global::System.Runtime.CompilerServices.Unsafe.AddByteOffset(ref obj, 8)))
				{
					do
					{
						VolumeData item = new VolumeData(ptr);
						list.Add(item);
						ptr = (common.system.VolumeData*)((long)(IntPtr)ptr + 104);
					}
					while (ptr != ptr2);
				}
				GC.KeepAlive(this);
			}
			catch
			{
				//try-fault
				_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<vector<common::system::VolumeData,std::allocator<common::system::VolumeData> >*, void>*/)(&_003CModule_003E.std_002Evector_003Ccommon_003A_003Asystem_003A_003AVolumeData_002Cstd_003A_003Aallocator_003Ccommon_003A_003Asystem_003A_003AVolumeData_003E_0020_003E_002E_007Bdtor_007D), &obj);
				throw;
			}
			_003CModule_003E.std_002Evector_003Ccommon_003A_003Asystem_003A_003AVolumeData_002Cstd_003A_003Aallocator_003Ccommon_003A_003Asystem_003A_003AVolumeData_003E_0020_003E_002E_Tidy(&obj);
			return list;
		}

		private unsafe void NotifyVolumesChanged(vector_003Ccommon_003A_003Asystem_003A_003AVolumeData_002Cstd_003A_003Aallocator_003Ccommon_003A_003Asystem_003A_003AVolumeData_003E_0020_003E* cameras)
		{
			//IL_0009: Expected I, but got I8
			//IL_000f: Expected I, but got I8
			//IL_0029: Expected I, but got I8
			List<VolumeData> list = new List<VolumeData>();
			common.system.VolumeData* ptr = (common.system.VolumeData*)(*(ulong*)cameras);
			common.system.VolumeData* ptr2 = (common.system.VolumeData*)(*(ulong*)((long)(IntPtr)cameras + 8));
			if (ptr != ptr2)
			{
				do
				{
					VolumeData item = new VolumeData(ptr);
					list.Add(item);
					ptr = (common.system.VolumeData*)((long)(IntPtr)ptr + 104);
				}
				while (ptr != ptr2);
			}
			if (mCallback != null)
			{
				_003Cbacking_store_003EOnVolumesChanged?.Invoke(this, list);
			}
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007EVolumeWatcher();
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
