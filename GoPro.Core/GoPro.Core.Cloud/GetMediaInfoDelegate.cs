using System.Runtime.InteropServices;
using GoPro.Core.Http;

namespace GoPro.Core.Cloud
{
	public delegate void GetMediaInfoDelegate(Error err, Response response, [MarshalAs(UnmanagedType.U1)] bool done, int currentPage, int totalPages);
}
