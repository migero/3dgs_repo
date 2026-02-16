using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Runtime.InteropServices;
using System.Runtime.Serialization;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using GoPro.Security;
using GoPro.Storage;
using GoPro.Utils;
using Microsoft.AppCenter.Crashes;

namespace GoPro.Instance
{
	public class CrashReporter
	{
		internal delegate int RecoveryDelegate(IntPtr parameterData);

		internal class ExceptionHash : Exception
		{
			private string mMessage;

			private Exception mException;

			public override string Source
			{
				get
				{
					return mException.Source;
				}
				set
				{
					mException.Source = value;
				}
			}

			public override string HelpLink
			{
				get
				{
					return mException.HelpLink;
				}
				set
				{
					mException.HelpLink = value;
				}
			}

			public override string StackTrace => mException.StackTrace;

			public override string Message => mMessage;

			public override IDictionary Data => mException.Data;

			public ExceptionHash(Exception exception)
			{
				mException = exception;
				if (mException.StackTrace != null)
				{
					byte[] bytes = Encoding.UTF8.GetBytes(mException.StackTrace);
					mMessage = Cryptography.ComputeHash(bytes);
				}
				else
				{
					mMessage = mException.Message;
				}
			}

			public override Exception GetBaseException()
			{
				return mException.GetBaseException();
			}

			public override void GetObjectData(SerializationInfo info, StreamingContext context)
			{
				mException.GetObjectData(info, context);
			}

			public override string ToString()
			{
				return mException.ToString();
			}
		}

		[Flags]
		private enum RestartRestrictions
		{
			None = 0,
			NotOnCrash = 1,
			NotOnHang = 2,
			NotOnPatch = 4,
			NotOnReboot = 8
		}

		public Action CaptureRecoveryRequested;

		public Func<Task<bool>> ReportStarted;

		public Action<uint> ReportUpdated;

		public Action<Exception, IList<ErrorAttachmentLog>> ReportFinished;

		internal static string RESTORE_ARG = "/Restore";

		internal static readonly uint RECOVERY_CALLBACK_INTERVAL = 5000u;

		public CrashReporter(bool recoverable = true)
		{
			if (recoverable)
			{
				RegisterApplicationRecoveryCallback(ApplicationRecoveryCallback, IntPtr.Zero, RECOVERY_CALLBACK_INTERVAL, 0u);
				RegisterApplicationRestart("", RestartRestrictions.None);
			}
		}

		public async Task GenerateReport(string userDirectory)
		{
			string dumpDirectory = Path.Combine(userDirectory, "Dumps");
			string[] dumpFiles = FileHelper.GetFilePaths(dumpDirectory, "*.dmp");
			if (dumpFiles == null || dumpFiles.Length == 0)
			{
				return;
			}
			bool generateReport = false;
			if (ReportStarted != null)
			{
				generateReport = await ReportStarted();
			}
			await Task.Run(delegate
			{
				if (generateReport)
				{
					if (ReportUpdated != null)
					{
						ReportUpdated(10u);
					}
					string text = dumpFiles[0];
					string message = "Unkown";
					MiniDump miniDump = new MiniDump();
					if (miniDump.Open(text))
					{
						string limitedStackTrace = miniDump.GetLimitedStackTrace();
						if (limitedStackTrace != null)
						{
							message = limitedStackTrace;
						}
						miniDump.Close();
					}
					if (ReportUpdated != null)
					{
						ReportUpdated(20u);
					}
					string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(text);
					string path = $"{fileNameWithoutExtension}.zip";
					string text2 = Path.Combine(userDirectory, path);
					if (File.Exists(text2))
					{
						File.Delete(text2);
					}
					ZipFile.CreateFromDirectory(dumpDirectory, text2);
					if (ReportUpdated != null)
					{
						ReportUpdated(40u);
					}
					List<ErrorAttachmentLog> list = new List<ErrorAttachmentLog>();
					byte[] array = File.ReadAllBytes(text2);
					File.Delete(text2);
					if (array.Length != 0)
					{
						AddAttachment(fileNameWithoutExtension, array, array.Length, list);
						if (ReportUpdated != null)
						{
							ReportUpdated(60u);
						}
						AddLogs(list, fileNameWithoutExtension, FileHelper.FilesSelection.All);
						if (ReportUpdated != null)
						{
							ReportUpdated(80u);
						}
					}
					if (ReportUpdated != null)
					{
						ReportUpdated(100u);
					}
					Exception arg = ((list.Count > 0) ? new Exception(message) : null);
					ReportFinished(arg, list);
				}
				if (Directory.Exists(dumpDirectory))
				{
					Directory.Delete(dumpDirectory, recursive: true);
				}
			});
		}

		public IList<ErrorAttachmentLog> GenerateLogAttachment(string name, FileHelper.FilesSelection selection)
		{
			IList<ErrorAttachmentLog> list = new List<ErrorAttachmentLog>();
			AddLogs(list, name, selection);
			return list;
		}

		public static void DispatchException(Exception exception, IList<ErrorAttachmentLog> attachments = null)
		{
			DateTime utcNow = DateTime.UtcNow;
			string text = utcNow.ToShortDateString() + " " + utcNow.ToShortTimeString() + " (UTC)";
			Dictionary<string, string> dictionary = new Dictionary<string, string>();
			dictionary.Add("Time", text);
			if (!string.IsNullOrWhiteSpace(exception.Message))
			{
				dictionary.Add("Message", exception.Message);
			}
			if (attachments == null)
			{
				attachments = new List<ErrorAttachmentLog>();
			}
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.AppendLine("Time: " + text + Environment.NewLine);
			stringBuilder.AppendLine(Log.GetVerboseExceptionSummary(exception));
			byte[] bytes = Encoding.ASCII.GetBytes(stringBuilder.ToString().TrimEnd(Array.Empty<char>()));
			attachments.Add(ErrorAttachmentLog.AttachmentWithBinary(bytes, "ExceptionDetails.txt", "application/octet-stream"));
			Crashes.TrackError(new ExceptionHash(exception), dictionary, attachments.ToArray());
		}

		private void AddLogs(IList<ErrorAttachmentLog> attachments, string logFileName, FileHelper.FilesSelection selection)
		{
			if (attachments == null)
			{
				return;
			}
			string logDirectory = FileHelper.GetLogDirectory();
			string text = Path.Combine(logDirectory, "Logs");
			if (FileHelper.DuplicateFolderFiles(logDirectory, text, FileHelper.LogFileExtension, selection) == null && Directory.Exists(text))
			{
				string text2 = $"{logFileName}.logs";
				string path = $"{text2}.zip";
				string text3 = Path.Combine(FileHelper.UserDirectory, path);
				ZipFile.CreateFromDirectory(text, text3);
				byte[] array = File.ReadAllBytes(text3);
				if (array.Length != 0)
				{
					AddAttachment(text2, array, array.Length, attachments);
				}
				Directory.Delete(text, recursive: true);
				File.Delete(text3);
			}
		}

		public void GenerateNativeIssue()
		{
			Environment.FailFast("Test Crash Native Layer");
		}

		public void GenerateAppIssue()
		{
			throw new Exception();
		}

		private int ApplicationRecoveryCallback(IntPtr parameterData)
		{
			if (CaptureRecoveryRequested != null)
			{
				bool captureDone = false;
				((DispatcherObject)Application.get_Current()).get_Dispatcher().InvokeAsync((Action)delegate
				{
					CaptureRecoveryRequested();
					captureDone = true;
				});
				while (!captureDone)
				{
					Thread.Sleep((int)(RECOVERY_CALLBACK_INTERVAL / 2u));
					ApplicationRecoveryInProgress(out captureDone);
				}
			}
			ApplicationRecoveryFinished(success: true);
			return 0;
		}

		private void AddAttachmentPart(string nameWithoutExtension, byte[] sourceData, int sourceOffset, int partSize, int index, IList<ErrorAttachmentLog> attachments)
		{
			byte[] array = new byte[partSize];
			Array.Copy(sourceData, sourceOffset, array, 0, partSize);
			string fileName = $"{nameWithoutExtension}.part{index}.zip";
			attachments.Add(ErrorAttachmentLog.AttachmentWithBinary(array, fileName, "application/octet-stream"));
		}

		private void AddAttachment(string nameWithoutExtension, byte[] sourceData, int totalSourceDataSize, IList<ErrorAttachmentLog> attachments)
		{
			int num = totalSourceDataSize;
			int num2 = 0;
			int num3 = 5242880;
			while (num > num3)
			{
				AddAttachmentPart(nameWithoutExtension, sourceData, num2 * num3, num3, num2, attachments);
				num -= num3;
				num2++;
			}
			if (num > 0)
			{
				AddAttachmentPart(nameWithoutExtension, sourceData, num2 * num3, num, num2, attachments);
			}
		}

		[DllImport("kernel32.dll")]
		private static extern int RegisterApplicationRecoveryCallback(RecoveryDelegate recoveryCallback, IntPtr parameter, uint pingInterval, uint flags);

		[DllImport("kernel32.dll")]
		private static extern int ApplicationRecoveryInProgress(out bool canceled);

		[DllImport("kernel32.dll")]
		private static extern void ApplicationRecoveryFinished(bool success);

		[DllImport("kernel32.dll")]
		private static extern int UnregisterApplicationRecoveryCallback();

		[DllImport("kernel32.dll")]
		private static extern int RegisterApplicationRestart([MarshalAs(UnmanagedType.LPWStr)] string commandLineArgs, RestartRestrictions flags);

		[DllImport("kernel32.dll")]
		private static extern int UnregisterApplicationRestart();
	}
}
