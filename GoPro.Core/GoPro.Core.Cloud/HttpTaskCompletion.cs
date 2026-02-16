using System;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using GoPro.Core.Http;
using std;

namespace GoPro.Core.Cloud
{
	[UnsafeValueType]
	internal class HttpTaskCompletion
	{
		private TaskCompletionSource<Response> mTaskCompletionSource;

		private unsafe NativeTaskCompletion* mTaskCompletion;

		public unsafe function_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E HttpCompletion
		{
			get
			{
				uint num = 0u;
				_003CModule_003E.GoPro_002ECore_002ECloud_002ENativeTaskCompletion_002EhttpCompletion(mTaskCompletion, P_0);
				try
				{
					num = 1u;
					GC.KeepAlive(this);
					return P_0;
				}
				catch
				{
					//try-fault
					if ((num & (true ? 1u : 0u)) != 0)
					{
						num &= 0xFFFFFFFEu;
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<function<void __cdecl(common::Error &,common::http::Request &,common::http::Response &)>*, void>*/)(&_003CModule_003E.std_002Efunction_003Cvoid_0020__cdecl_0028common_003A_003AError_0020_0026_002Ccommon_003A_003Ahttp_003A_003ARequest_0020_0026_002Ccommon_003A_003Ahttp_003A_003AResponse_0020_0026_0029_003E_002E_007Bdtor_007D), P_0);
					}
					throw;
				}
			}
		}

		public Task<Response> CompletionTask
		{
			get
			{
				Task<Response> task = mTaskCompletionSource.Task;
				GC.KeepAlive(this);
				return task;
			}
		}

		public unsafe HttpTaskCompletion()
		{
			//IL_0044: Expected I, but got I8
			//IL_006d: Expected I, but got I8
			//IL_0084: Expected I, but got I8
			mTaskCompletionSource = new TaskCompletionSource<Response>();
			NativeTaskCompletion* ptr = (NativeTaskCompletion*)_003CModule_003E.@new(16uL);
			NativeTaskCompletion* ptr3;
			try
			{
				if (ptr != null)
				{
					Action<Exception> t = OnError;
					Action<Response> t2 = OnResult;
					_003CModule_003E.gcroot_003CSystem_003A_003AAction_003CGoPro_003A_003ACore_003A_003AHttp_003A_003AResponse_0020_005E_003E_0020_005E_003E_002E_007Bctor_007D((gcroot_003CSystem_003A_003AAction_003CGoPro_003A_003ACore_003A_003AHttp_003A_003AResponse_0020_005E_003E_0020_005E_003E*)ptr);
					try
					{
						NativeTaskCompletion* ptr2 = (NativeTaskCompletion*)((long)(IntPtr)ptr + 8);
						_003CModule_003E.gcroot_003CSystem_003A_003AAction_003CSystem_003A_003AException_0020_005E_003E_0020_005E_003E_002E_007Bctor_007D((gcroot_003CSystem_003A_003AAction_003CSystem_003A_003AException_0020_005E_003E_0020_005E_003E*)ptr2);
						try
						{
							_003CModule_003E.gcroot_003CSystem_003A_003AAction_003CGoPro_003A_003ACore_003A_003AHttp_003A_003AResponse_0020_005E_003E_0020_005E_003E_002E_003D((gcroot_003CSystem_003A_003AAction_003CGoPro_003A_003ACore_003A_003AHttp_003A_003AResponse_0020_005E_003E_0020_005E_003E*)ptr, t2);
							_003CModule_003E.gcroot_003CSystem_003A_003AAction_003CSystem_003A_003AException_0020_005E_003E_0020_005E_003E_002E_003D((gcroot_003CSystem_003A_003AAction_003CSystem_003A_003AException_0020_005E_003E_0020_005E_003E*)ptr2, t);
						}
						catch
						{
							//try-fault
							_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<gcroot<System::Action<System::Exception ^> ^>*, void>*/)(&_003CModule_003E.gcroot_003CSystem_003A_003AAction_003CSystem_003A_003AException_0020_005E_003E_0020_005E_003E_002E_007Bdtor_007D), (void*)((long)(IntPtr)ptr + 8));
							throw;
						}
					}
					catch
					{
						//try-fault
						_003CModule_003E.___CxxCallUnwindDtor((UIntPtr/*delegate*<void*, void>*/)(void*)(ulong)(UIntPtr/*delegate*<gcroot<System::Action<GoPro::Core::Http::Response ^> ^>*, void>*/)(&_003CModule_003E.gcroot_003CSystem_003A_003AAction_003CGoPro_003A_003ACore_003A_003AHttp_003A_003AResponse_0020_005E_003E_0020_005E_003E_002E_007Bdtor_007D), ptr);
						throw;
					}
					ptr3 = ptr;
				}
				else
				{
					ptr3 = null;
				}
			}
			catch
			{
				//try-fault
				_003CModule_003E.delete(ptr, 16uL);
				throw;
			}
			mTaskCompletion = ptr3;
			GC.KeepAlive(this);
		}

		public void OnResult(Response response)
		{
			mTaskCompletionSource.SetResult(response);
			GC.KeepAlive(this);
		}

		public void OnError(Exception ex)
		{
			mTaskCompletionSource.SetException(ex);
			GC.KeepAlive(this);
		}
	}
}
