using System.Diagnostics;
using System.Windows.Documents;

namespace GoPro.Controls
{
	public class AutoNavigateHyperlink : Hyperlink
	{
		protected override void OnClick()
		{
			Process.Start(new ProcessStartInfo(((Hyperlink)this).get_NavigateUri().AbsoluteUri));
		}
	}
}
