using System.Diagnostics;

namespace GoPro.Utils
{
	public class ReviewChecker
	{
		public delegate bool ReviewRequestedDelegate();

		private string m_ApplicationID;

		private string m_LastVersionReviewRequested;

		private int[] m_ActionsDone;

		private int[] m_ActionsThreshold;

		public event ReviewRequestedDelegate ReviewRequested;

		public void Initialize(string applicationId, string lastVersionReviewRequested, int[] actionsDone, int[] actionsThreshold)
		{
			m_ApplicationID = applicationId;
			m_LastVersionReviewRequested = lastVersionReviewRequested;
			m_ActionsDone = actionsDone;
			m_ActionsThreshold = actionsThreshold;
		}

		public void Release()
		{
			m_LastVersionReviewRequested = null;
			m_ActionsDone = null;
			m_ActionsThreshold = null;
		}

		public void AddAction(uint action)
		{
			m_ActionsDone[action]++;
			if (ShouldRequestReview())
			{
				m_LastVersionReviewRequested = AssemblyHelper.Version;
				if (this.ReviewRequested != null && this.ReviewRequested())
				{
					Process.Start($"ms-windows-store://review/?ProductId={m_ApplicationID}");
				}
			}
		}

		private bool ShouldRequestReview()
		{
			if (m_LastVersionReviewRequested != null && AssemblyHelper.CheckVersionState(m_LastVersionReviewRequested, 2) != AssemblyHelper.AssemblyVersionState.OLDER)
			{
				return false;
			}
			if (IsActionDone())
			{
				return true;
			}
			return false;
		}

		private bool IsActionDone()
		{
			if (m_ActionsDone.Length <= m_ActionsThreshold.Length)
			{
				for (int i = 0; i < m_ActionsDone.Length; i++)
				{
					if (m_ActionsDone[i] >= m_ActionsThreshold[i])
					{
						return true;
					}
				}
			}
			return false;
		}
	}
}
