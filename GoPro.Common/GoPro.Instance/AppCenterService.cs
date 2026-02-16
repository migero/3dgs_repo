using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Reflection;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows;
using System.Windows.Threading;
using Microsoft.AppCenter;
using Microsoft.AppCenter.Analytics;
using Microsoft.AppCenter.Crashes;
using Newtonsoft.Json;

namespace GoPro.Instance
{
	public class AppCenterService
	{
		public struct ReleaseDesc
		{
			public string Version;

			public uint Size;

			public string Notes;

			public string Url;

			public string FingerPrint;
		}

		public delegate void ReleaseDescFinishedDelegate(ReleaseDesc? releaseDesc);

		public delegate void DownloadFileProgressedDelegate(long bytes, long totalBytes);

		public delegate void DownloadFileFinishedDelegate();

		public delegate void RequestFinishedDelegate(StreamReader stream, long totalBytes, object[] arguments);

		internal struct WebRequestHandle
		{
			public HttpWebRequest Request;

			public RequestFinishedDelegate Callback;

			public object[] Arguments;
		}

		internal struct FileRequestHandle
		{
			public Stream Stream;

			public byte[] Buffer;

			public Stream Destination;

			public long Bytes;

			public long TotalBytes;

			public DownloadFileProgressedDelegate Progressed;

			public DownloadFileFinishedDelegate Finished;
		}

		private static string mKey;

		private const string BASE_URL = "https://api.appcenter.ms/v0.1/public/sdk/apps";

		public static string Key
		{
			get
			{
				return mKey;
			}
			set
			{
				if (mKey == null)
				{
					mKey = value;
					if (mKey != null)
					{
						AppCenter.Start(mKey, typeof(Microsoft.AppCenter.Analytics.Analytics), typeof(Crashes));
					}
				}
			}
		}

		public static void SetAllowAnalytics(bool allowAnalytics)
		{
			if (!allowAnalytics)
			{
				Microsoft.AppCenter.Analytics.Analytics.SetEnabledAsync(enabled: false);
			}
			else
			{
				Microsoft.AppCenter.Analytics.Analytics.SetEnabledAsync(enabled: true);
			}
		}

		public static void TrackAnalyticsEvent(string name, IDictionary<string, string> properties)
		{
			Microsoft.AppCenter.Analytics.Analytics.TrackEvent(name, properties);
		}

		public static void GetLastReleaseAsync(ReleaseDescFinishedDelegate callback)
		{
			SendRequest("releases/latest", GetLastReleaseIdAsyncInternal, new object[1] { callback });
		}

		public static void SendRequest(string endpoint, RequestFinishedDelegate callback, object[] arguments)
		{
			if (Key != null)
			{
				CreateRequest(string.Format("{0}/{1}/{2}", "https://api.appcenter.ms/v0.1/public/sdk/apps", Key, endpoint), callback, arguments);
			}
		}

		public static void DownloadFileAsync(string url, string destination, DownloadFileProgressedDelegate progressCallback, DownloadFileFinishedDelegate finishedCallback)
		{
			CreateRequest(url, DownloadFileAsyncRequestFinished, new object[3] { destination, progressCallback, finishedCallback });
		}

		private static void GetLastReleaseIdAsyncInternal(StreamReader stream, long totalBytes, object[] arguments)
		{
			ReleaseDescFinishedDelegate callback = (ReleaseDescFinishedDelegate)arguments[0];
			dynamic val = JsonConvert.DeserializeObject(stream.ReadToEnd());
			if (val == null)
			{
				callback(null);
				return;
			}
			Match match = Regex.Match(val.version, "\\d+(?:\\.\\d+)+");
			if (!match.Success)
			{
				return;
			}
			string version = ((AssemblyFileVersionAttribute)Assembly.GetEntryAssembly()!.GetCustomAttributes(typeof(AssemblyFileVersionAttribute), inherit: false)[0]).Version;
			string[] array = match.Value.Split(new char[1] { '.' });
			string[] array2 = version.Split(new char[1] { '.' });
			if (array2.Length != array.Length)
			{
				return;
			}
			for (int i = 0; i < array2.Length; i++)
			{
				uint num = uint.Parse(array2[i]);
				uint num2 = uint.Parse(array[i]);
				if (num > num2)
				{
					break;
				}
				if (num < num2)
				{
					ReleaseDesc desc = default(ReleaseDesc);
					desc.Version = val.version;
					desc.Size = val.size;
					if (val.release_notes != null)
					{
						Encoding uTF = Encoding.UTF8;
						byte[] bytes = uTF.GetBytes((string)val.release_notes);
						desc.Notes = uTF.GetString(bytes, 0, bytes.Length);
					}
					desc.Url = val.download_url;
					desc.FingerPrint = val.fingerprint;
					((DispatcherObject)Application.get_Current()).get_Dispatcher().Invoke((Action)delegate
					{
						callback(desc);
					});
					break;
				}
			}
		}

		internal static void DownloadFileAsyncRequestFinished(StreamReader stream, long totalBytes, object[] arguments)
		{
			int num = 16384;
			string path = (string)arguments[0];
			if (File.Exists(path))
			{
				File.Delete(path);
			}
			FileRequestHandle fileRequestHandle = default(FileRequestHandle);
			fileRequestHandle.Stream = stream.BaseStream;
			fileRequestHandle.Buffer = new byte[num];
			fileRequestHandle.Destination = new FileStream(path, FileMode.CreateNew);
			fileRequestHandle.Progressed = (DownloadFileProgressedDelegate)arguments[1];
			fileRequestHandle.Finished = (DownloadFileFinishedDelegate)arguments[2];
			fileRequestHandle.Bytes = 0L;
			fileRequestHandle.TotalBytes = totalBytes;
			stream.BaseStream.BeginRead(fileRequestHandle.Buffer, 0, num, ReadStreamCallback, fileRequestHandle);
		}

		internal static void ReadStreamCallback(IAsyncResult iAsyncResult)
		{
			FileRequestHandle fileRequestHandle = (FileRequestHandle)iAsyncResult.AsyncState;
			int num = fileRequestHandle.Stream.EndRead(iAsyncResult);
			if (num > 0)
			{
				fileRequestHandle.Bytes += num;
				fileRequestHandle.Destination.Write(fileRequestHandle.Buffer, 0, num);
				((DispatcherObject)Application.get_Current()).get_Dispatcher().Invoke((Action)delegate
				{
					fileRequestHandle.Progressed(fileRequestHandle.Bytes, fileRequestHandle.TotalBytes);
				});
				fileRequestHandle.Stream.BeginRead(fileRequestHandle.Buffer, 0, fileRequestHandle.Buffer.Length, ReadStreamCallback, fileRequestHandle);
			}
			else
			{
				fileRequestHandle.Destination.Close();
				((DispatcherObject)Application.get_Current()).get_Dispatcher().Invoke((Action)delegate
				{
					fileRequestHandle.Finished();
				});
			}
		}

		internal static void CreateRequest(string url, RequestFinishedDelegate callback, object[] arguments)
		{
			HttpWebRequest httpWebRequest = WebRequest.CreateHttp(url);
			httpWebRequest.Method = "GET";
			httpWebRequest.BeginGetResponse(WebRequestCallback, new WebRequestHandle
			{
				Request = httpWebRequest,
				Callback = callback,
				Arguments = arguments
			});
		}

		internal static void WebRequestCallback(IAsyncResult asynchronousResult)
		{
			try
			{
				WebRequestHandle webRequestHandle = (WebRequestHandle)asynchronousResult.AsyncState;
				WebResponse webResponse = webRequestHandle.Request.EndGetResponse(asynchronousResult);
				StreamReader stream = new StreamReader(webResponse.GetResponseStream());
				webRequestHandle.Callback(stream, webResponse.ContentLength, webRequestHandle.Arguments);
			}
			catch
			{
			}
		}
	}
}
