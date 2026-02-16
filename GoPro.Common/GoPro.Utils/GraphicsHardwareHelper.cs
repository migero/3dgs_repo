using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Management;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using GoPro.Storage;
using Newtonsoft.Json;

namespace GoPro.Utils
{
	public class GraphicsHardwareHelper
	{
		private static readonly string DOWNLOAD_ADDRESS = "https://static.gopro-qa.com/desktop/DriverList.json";

		private static readonly string LOCAL_DRIVER_LIST_FILEPATH = Path.Combine(FileHelper.UserDirectory, "DriverList.json");

		private static List<VideoController> mVideoControllers = null;

		public static async Task<List<VideoController>> GetOrCreateVideoControllers()
		{
			if (mVideoControllers != null)
			{
				return mVideoControllers.ToList();
			}
			List<VideoController> list;
			try
			{
				ManagementObjectSearcher val = new ManagementObjectSearcher("select * from Win32_VideoController");
				list = new List<VideoController>();
				ManagementObjectEnumerator enumerator = val.Get().GetEnumerator();
				try
				{
					while (enumerator.MoveNext())
					{
						ManagementObject obj = (ManagementObject)enumerator.get_Current();
						list.Add(new VideoController(obj));
					}
				}
				finally
				{
					((IDisposable)enumerator)?.Dispose();
				}
			}
			catch
			{
				return null;
			}
			mVideoControllers = list;
			await ApplyDriverInfos(list);
			return mVideoControllers.ToList();
		}

		public static async Task<VideoController> GetVideoController(ulong deviceId)
		{
			return (await GetOrCreateVideoControllers())?.Find((VideoController vc) => vc.DeviceId == deviceId);
		}

		private static async Task<bool> ApplyDriverInfos(List<VideoController> videoControllers)
		{
			if (!(await DownloadDriverList()))
			{
				return false;
			}
			AvailableGraphicsDrivers availableGraphicsDrivers;
			try
			{
				availableGraphicsDrivers = JsonConvert.DeserializeObject(File.ReadAllText(LOCAL_DRIVER_LIST_FILEPATH), typeof(AvailableGraphicsDrivers)) as AvailableGraphicsDrivers;
			}
			catch (Exception)
			{
				return false;
			}
			if (availableGraphicsDrivers == null)
			{
				return false;
			}
			foreach (VideoController videoController in videoControllers)
			{
				videoController.QueryLatestDriverVersion(availableGraphicsDrivers);
			}
			return true;
		}

		private static async Task<bool> DownloadDriverList()
		{
			if (!Uri.TryCreate(DOWNLOAD_ADDRESS, UriKind.Absolute, out var downloadAddressUri))
			{
				return false;
			}
			if (await IsRemoteDriverListNew(downloadAddressUri))
			{
				WebClient webClient = new WebClient();
				try
				{
					await webClient.DownloadFileTaskAsync(downloadAddressUri, LOCAL_DRIVER_LIST_FILEPATH);
				}
				catch (Exception)
				{
					return false;
				}
			}
			return true;
		}

		private static async Task<bool> IsRemoteDriverListNew(Uri downloadAddressUri)
		{
			if (File.Exists(LOCAL_DRIVER_LIST_FILEPATH))
			{
				FileInfo fileInfo = new FileInfo(LOCAL_DRIVER_LIST_FILEPATH);
				if (fileInfo.Length == 0L)
				{
					return true;
				}
				HttpClient val = new HttpClient();
				try
				{
					HttpResponseMessage val2 = await val.SendAsync(new HttpRequestMessage(HttpMethod.get_Head(), downloadAddressUri));
					if (val2.get_IsSuccessStatusCode())
					{
						DateTime dateTime = val2.get_Content().get_Headers().get_LastModified()
							.Value.DateTime;
						DateTime lastWriteTimeUtc = fileInfo.LastWriteTimeUtc;
						return dateTime > lastWriteTimeUtc;
					}
					return false;
				}
				catch (Exception)
				{
					return false;
				}
			}
			return true;
		}
	}
}
