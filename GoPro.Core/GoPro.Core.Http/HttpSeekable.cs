using System;

namespace GoPro.Core.Http
{
	public class HttpSeekable : Seekable
	{
		public HttpSeekable(Session A_0, Uri A_1)
		{
			uint num = 0u;
			((object)this)._002Ector();
			try
			{
				IntPtr intPtr2 = (base.Pointer = _003CModule_003E.GoPro_002ECore_002EHttp_002EcreateSeekablePtr(A_0, A_1.ToString()));
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

		public HttpSeekable(Session A_0, Url A_1)
		{
			//Discarded unreachable code: IL_004e
			uint num = 0u;
			((object)this)._002Ector();
			try
			{
				if (A_1 != null && !string.IsNullOrEmpty(A_1.ToString()))
				{
					IntPtr intPtr2 = (base.Pointer = _003CModule_003E.GoPro_002ECore_002EHttp_002EcreateSeekablePtr(A_0, A_1.ToString()));
					GC.KeepAlive(this);
					goto IL_0058;
				}
			}
			catch
			{
				//try-fault
				base.Dispose(A_0: true);
				throw;
			}
			try
			{
				throw new ArgumentNullException("invalid url");
			}
			catch
			{
				//try-fault
				base.Dispose(A_0: true);
				throw;
			}
			IL_0058:
			try
			{
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
